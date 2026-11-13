"""Smoke checks for the KWin Ryzen default variant and debug fallback.

For actual upstream patch validation:
KWIN_UPSTREAM_TREE=/path/to/KDE/kwin-v6.8.1 pytest -q tests/test_kwin_zen2.py
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "--KDE--/kwin/kwin.lpmbuild"
PATCHES = (
    "0001-kwin-blur-cache-clip-transforms.patch",
    "0002-kwin-blur-share-kawase-projection.patch",
)
PATCH_DIR = ROOT / "--KDE--/kwin"


def read_metadata(profile=None):
    env = os.environ.copy()
    env.pop("LPM_KWIN_PROFILE", None)
    if profile:
        env["LPM_KWIN_PROFILE"] = profile
    return subprocess.run(
        ["bash", "-c",
         'source "$1" || exit $?; printf "RELEASE=%s\n" "$RELEASE"; '
         'printf "PROFILE=%s\n" "$KWIN_LPM_PROFILE"; '
         'declare -p PATCHES', "test", str(RECIPE)],
        env=env, capture_output=True, text=True,
    )


def test_recipe_shell_and_profile_selection():
    subprocess.run(["bash", "-n", str(RECIPE)], check=True)
    base = read_metadata()
    assert base.returncode == 0, base.stderr
    assert "RELEASE=4" in base.stdout
    assert "PROFILE=zen2" in base.stdout
    for patch in PATCHES:
        assert patch in base.stdout

    debug = read_metadata("debug")
    assert debug.returncode == 0, debug.stderr
    assert "RELEASE=3" in debug.stdout
    assert "PROFILE=debug" in debug.stdout
    assert 'PATCHES=()' in debug.stdout

    fast = read_metadata("zen2")
    assert fast.returncode == 0, fast.stderr
    assert "RELEASE=4" in fast.stdout
    assert "PROFILE=zen2" in fast.stdout
    for patch in PATCHES:
        assert patch in fast.stdout
        assert (PATCH_DIR / patch).is_file()

    invalid = read_metadata("bad-profile")
    assert invalid.returncode != 0
    assert "Unknown LPM_KWIN_PROFILE" in invalid.stderr


def test_optimized_recipe_preserves_abi_and_recovery():
    text = RECIPE.read_text(encoding="utf-8")
    assert "-march=znver2" in text
    assert "-mtune=znver2" in text
    assert "-O2" in text
    assert "-fno-omit-frame-pointer" in text
    assert "CMAKE_INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO:BOOL" in text
    assert "-DBUILD_SHARED_LIBS=ON" in text
    assert "-DKWIN_BUILD_SCREENLOCKER=ON" in text
    assert "-DKWIN_BUILD_X11=ON" in text
    assert "-ffast-math" not in text.replace(
        "# Avoid -Ofast/-ffast-math: KWin geometry and HDR need IEEE semantics.",
        "",
    )


def test_blur_optimizations_apply_to_exact_upstream_681():
    upstream = os.environ.get("KWIN_UPSTREAM_TREE")
    if not upstream:
        return  # GitHub CI supplies KDE/kwin at tag v6.8.1.
    original = Path(upstream) / "src/plugins/blur/blur.cpp"
    assert original.is_file(), original
    with tempfile.TemporaryDirectory() as d:
        staged = Path(d) / "src/plugins/blur/blur.cpp"
        staged.parent.mkdir(parents=True)
        shutil.copy2(original, staged)
        for patch in PATCHES:
            subprocess.run(
                ["patch", "--batch", "--forward", "-p1",
                 "--dry-run", "-i", str(PATCH_DIR / patch)],
                cwd=d, check=True, capture_output=True, text=True,
            )
            subprocess.run(
                ["patch", "--batch", "--forward", "-p1",
                 "-i", str(PATCH_DIR / patch)],
                cwd=d, check=True, capture_output=True, text=True,
            )
        result = staged.read_text(encoding="utf-8")
        assert "deviceShapeRects.reserve(shapeRects.size())" in result
        assert "const auto clipRects = deviceRegion.rects()" in result
        assert "for (const RectF &deviceShapeRect : deviceShapeRects)" in result
        assert result.count("offscreenProjectionMatrix.ortho(") == 1
        assert "m_downsamplePass.mvpMatrixLocation, offscreenProjectionMatrix" in result
        assert "m_upsamplePass.mvpMatrixLocation, offscreenProjectionMatrix" in result


def test_no_undefined_ninja_link_pool():
    """Regression guard: CMake does not define pools via CMAKE_JOB_POOLS."""
    recipe = RECIPE.read_text(encoding="utf-8")
    assert "-DCMAKE_JOB_POOLS" not in recipe
    assert "-DCMAKE_JOB_POOL_LINK" not in recipe
