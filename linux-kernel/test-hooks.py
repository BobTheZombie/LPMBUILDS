#!/usr/bin/env python3
"""Isolated tests; never invokes real bootctl, depmod or mkinitcpio."""
import configparser
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

loader = importlib.machinery.SourceFileLoader('linux_maintain', str(Path(__file__).with_name('linux-maintain')))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)


class HookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'root'
        self.esp = Path(self.tmp.name)/'esp'
        self.root.mkdir(); self.esp.mkdir()
        self.version = '7.2.11-lpm1'
        directory = self.root/'usr/lib/modules'/self.version
        directory.mkdir(parents=True)
        (directory/'vmlinuz').write_bytes(b'kernel')
        (directory/'pkgbase').write_text('linux\n')
        (self.root/'boot').mkdir()
        (self.root/'boot'/f'initrd-{self.version}.img').write_bytes(b'good-initrd')
        cmdline = self.root/'cmdline'
        cmdline.write_text('root=UUID=TEST rw\n')
        self.config = configparser.ConfigParser()
        self.config.read_dict({'boot':{'enabled':'true','esp':str(self.esp),'cmdline':str(cmdline)}})

    def boot(self):
        with patch.object(m.os.path,'ismount',return_value=True), \
             patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],0)), \
             patch.object(m,'run') as runner:
            m.update_boot(self.root,self.config)
        return runner

    def test_create_and_preserve_policy(self):
        self.boot()
        entry=self.esp/'loader/entries'/f'lpm-linux-{self.version}.conf'
        self.assertTrue(entry.read_text().startswith(m.MARKER))
        self.assertIn('root=UUID=TEST rw',entry.read_text())
        loader=self.esp/'loader/loader.conf'; loader.write_text('default rescue\n')
        self.boot(); self.assertEqual(loader.read_text(),'default rescue\n')
        self.assertEqual((self.esp/'lpm-kernels'/self.version/'vmlinuz').read_bytes(),b'kernel')

    def test_remove_only_owned_entry(self):
        self.boot()
        entries=self.esp/'loader/entries'
        unmanaged=entries/'lpm-linux-rescue.conf';unmanaged.write_text('title My rescue\n')
        old=entries/'lpm-linux-7.1-lpm1.conf';old.write_text(m.MARKER+'title old\n')
        self.boot()
        self.assertFalse(old.exists());self.assertTrue(unmanaged.exists())

    def test_missing_initrd_preserves_existing_esp(self):
        self.boot()
        entry=self.esp/'loader/entries'/f'lpm-linux-{self.version}.conf'; previous=entry.read_bytes()
        (self.root/'boot'/f'initrd-{self.version}.img').unlink()
        with self.assertRaisesRegex(RuntimeError,'Missing initramfs'):
            self.boot()
        self.assertEqual(entry.read_bytes(),previous)

    def test_unmanaged_entry_not_overwritten(self):
        entry=self.esp/'loader/entries'/f'lpm-linux-{self.version}.conf'
        entry.parent.mkdir(parents=True);entry.write_text('title custom\n')
        with self.assertRaisesRegex(RuntimeError,'unmanaged'):
            self.boot()

    def test_symlink_escape_rejected(self):
        (self.esp/'lpm-kernels').symlink_to(self.root,target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError,'escapes ESP'):
            self.boot()

    def test_initramfs_failure_preserves_image(self):
        with patch.object(m,'run',side_effect=subprocess.CalledProcessError(1,['test'])):
            with self.assertRaises(subprocess.CalledProcessError):
                m.initramfs(self.root,{self.version})
        self.assertEqual((self.root/'boot'/f'initrd-{self.version}.img').read_bytes(),b'good-initrd')

    def test_mkinitcpio_failure_after_depmod_preserves_image(self):
        def failing(command):
            if command[0]=='mkinitcpio':raise subprocess.CalledProcessError(1,command)
        with patch.object(m,'run',side_effect=failing):
            with self.assertRaises(subprocess.CalledProcessError):m.initramfs(self.root,{self.version})
        self.assertEqual((self.root/'boot'/f'initrd-{self.version}.img').read_bytes(),b'good-initrd')

    def test_target_removal_does_not_delete_other_kernel_initrd(self):
        image=self.root/'boot/initrd-foreign.img';image.write_bytes(b'keep')
        m.initramfs(self.root,{'foreign'})
        self.assertEqual(image.read_bytes(),b'keep')
        removed=self.root/'boot/initrd-7.1-lpm1.img';removed.write_bytes(b'old')
        m.initramfs(self.root,{'7.1-lpm1'});self.assertFalse(removed.exists())

    def test_targets_and_alternate_root(self):
        with patch.dict(os.environ,{'LPM_TARGETS':'usr/lib/modules/7.2.11-lpm1/vmlinuz','LPM_TARGETS_FILE':'','LPM_ROOT':str(self.root)}):
            self.assertEqual(m.targets([]),{self.version})
            with patch.object(m,'run') as runner:
                self.assertEqual(m.main(['--initramfs','--boot']),0)
                runner.assert_not_called()

    def test_disabled_configuration_does_nothing(self):
        self.config.set('boot','enabled','false')
        with patch.object(m,'run') as runner:
            m.update_boot(self.root,self.config)
            runner.assert_not_called()


if __name__=='__main__':unittest.main()
