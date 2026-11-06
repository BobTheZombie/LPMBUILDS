/* LPM Linux PackageKit backend (PackageKit 1.4.0 spawn API).
 * SPDX-License-Identifier: GPL-2.0-or-later
 * All package operations delegate to the LPM helper and /usr/bin/lpm.
 */
#include <pk-backend.h>
#include <pk-backend-spawn.h>

static PkBackendSpawn *lpm_spawn = NULL;
#define HELPER "lpmBackend.py"

void pk_backend_initialize(GKeyFile *conf, PkBackend *backend)
{
    lpm_spawn = pk_backend_spawn_new(conf);
    pk_backend_spawn_set_name(lpm_spawn, "lpm");
    pk_backend_spawn_set_allow_sigkill(lpm_spawn, FALSE);
}

void pk_backend_destroy(PkBackend *backend)
{
    g_clear_object(&lpm_spawn);
}

void pk_backend_start_job(PkBackend *backend, PkBackendJob *job)
{
    if (pk_backend_spawn_is_busy(lpm_spawn)) {
        pk_backend_job_error_code(job, PK_ERROR_ENUM_LOCK_REQUIRED, "LPM backend is busy");
        pk_backend_job_finished(job);
    }
}

PkBitfield pk_backend_get_groups(PkBackend *backend)
{
    return pk_bitfield_from_enums(PK_GROUP_ENUM_UNKNOWN, PK_GROUP_ENUM_SYSTEM,
                                  PK_GROUP_ENUM_DESKTOP_KDE, PK_GROUP_ENUM_PROGRAMMING,
                                  PK_GROUP_ENUM_MULTIMEDIA, -1);
}

PkBitfield pk_backend_get_filters(PkBackend *backend)
{
    return pk_bitfield_from_enums(PK_FILTER_ENUM_INSTALLED,
                                  PK_FILTER_ENUM_NOT_INSTALLED, -1);
}

PkBitfield pk_backend_get_roles(PkBackend *backend)
{
    /* No offline-update or simulation roles until supported by LPM. */
    return pk_bitfield_from_enums(
        PK_ROLE_ENUM_GET_PACKAGES, PK_ROLE_ENUM_SEARCH_NAME,
        PK_ROLE_ENUM_SEARCH_DETAILS, PK_ROLE_ENUM_RESOLVE,
        PK_ROLE_ENUM_GET_DETAILS, PK_ROLE_ENUM_GET_UPDATES,
        PK_ROLE_ENUM_INSTALL_PACKAGES, PK_ROLE_ENUM_INSTALL_FILES,
        PK_ROLE_ENUM_REMOVE_PACKAGES,
        PK_ROLE_ENUM_UPDATE_PACKAGES, PK_ROLE_ENUM_REFRESH_CACHE, -1);
}

void pk_backend_get_packages(PkBackend *backend, PkBackendJob *job, PkBitfield filters)
{
    gchar *f = pk_filter_bitfield_to_string(filters);
    pk_backend_spawn_helper(lpm_spawn, job, HELPER, "get-packages", f, NULL);
    g_free(f);
}

void pk_backend_search_names(PkBackend *backend, PkBackendJob *job, PkBitfield filters, gchar **values)
{
    gchar *f = pk_filter_bitfield_to_string(filters);
    gchar *terms = g_strjoinv("&", values);
    pk_backend_spawn_helper(lpm_spawn, job, HELPER, "search-name", f, terms, NULL);
    g_free(f);
    g_free(terms);
}

void pk_backend_search_details(PkBackend *backend, PkBackendJob *job, PkBitfield filters, gchar **values)
{
    gchar *f = pk_filter_bitfield_to_string(filters);
    gchar *terms = g_strjoinv("&", values);
    pk_backend_spawn_helper(lpm_spawn, job, HELPER, "search-details", f, terms, NULL);
    g_free(f);
    g_free(terms);
}

void pk_backend_resolve(PkBackend *backend, PkBackendJob *job, PkBitfield filters, gchar **package_ids)
{
    gchar *f = pk_filter_bitfield_to_string(filters);
    gchar *ids = pk_package_ids_to_string(package_ids);
    pk_backend_spawn_helper(lpm_spawn, job, HELPER, "resolve", f, ids, NULL);
    g_free(f);
    g_free(ids);
}

void pk_backend_get_details(PkBackend *backend, PkBackendJob *job, gchar **package_ids)
{
    gchar *ids = pk_package_ids_to_string(package_ids);
    pk_backend_spawn_helper(lpm_spawn, job, HELPER, "get-details", ids, NULL);
    g_free(ids);
}

void pk_backend_get_updates(PkBackend *backend, PkBackendJob *job, PkBitfield filters)
{
    gchar *f = pk_filter_bitfield_to_string(filters);
    pk_backend_spawn_helper(lpm_spawn, job, HELPER, "get-updates", f, NULL);
    g_free(f);
}

void pk_backend_install_packages(PkBackend *backend, PkBackendJob *job,
                                 PkBitfield flags, gchar **package_ids)
{
    gchar *f = pk_transaction_flag_bitfield_to_string(flags);
    gchar *ids = pk_package_ids_to_string(package_ids);
    pk_backend_spawn_helper(lpm_spawn, job, HELPER, "install-packages", f, ids, NULL);
    g_free(f);
    g_free(ids);
}

/* PackageKit InstallFiles -> helper -> signed LPM installpkg --verify. */
void pk_backend_install_files(PkBackend *backend, PkBackendJob *job,
                              PkBitfield flags, gchar **full_paths)
{
    gchar *f = pk_transaction_flag_bitfield_to_string(flags);
    gchar *paths = g_strjoinv("|", full_paths);
    pk_backend_spawn_helper(lpm_spawn, job, HELPER, "install-files", f, paths, NULL);
    g_free(f);
    g_free(paths);
}

gchar **pk_backend_get_mime_types(PkBackend *backend)
{
    const gchar *mime_types[] = { "application/zstd", "application/x-zstd", NULL };
    return g_strdupv((gchar **)mime_types);
}

void pk_backend_remove_packages(PkBackend *backend, PkBackendJob *job,
                                PkBitfield flags, gchar **package_ids,
                                gboolean allow_deps, gboolean autoremove)
{
    gchar *f = pk_transaction_flag_bitfield_to_string(flags);
    gchar *ids = pk_package_ids_to_string(package_ids);
    pk_backend_spawn_helper(lpm_spawn, job, HELPER, "remove-packages", f, ids,
                            pk_backend_bool_to_string(allow_deps),
                            pk_backend_bool_to_string(autoremove), NULL);
    g_free(f);
    g_free(ids);
}

void pk_backend_update_packages(PkBackend *backend, PkBackendJob *job,
                                PkBitfield flags, gchar **package_ids)
{
    gchar *f = pk_transaction_flag_bitfield_to_string(flags);
    gchar *ids = pk_package_ids_to_string(package_ids);
    pk_backend_spawn_helper(lpm_spawn, job, HELPER, "update-packages", f, ids, NULL);
    g_free(f);
    g_free(ids);
}

void pk_backend_refresh_cache(PkBackend *backend, PkBackendJob *job, gboolean force)
{
    pk_backend_spawn_helper(lpm_spawn, job, HELPER, "refresh-cache",
                            pk_backend_bool_to_string(force), NULL);
}

const gchar *pk_backend_get_description(PkBackend *backend)
{
    return "LPM Linux native package manager";
}

const gchar *pk_backend_get_author(PkBackend *backend)
{
    return "LPM Linux contributors";
}

gboolean pk_backend_supports_parallelization(PkBackend *backend)
{
    return FALSE;
}
