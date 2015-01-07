from django.conf.urls import patterns, include, url
#from integral_view.views.iscsi import iscsi_display_global_config, iscsi_display_initiators, iscsi_display_targets, iscsi_view_initiator, iscsi_edit_initiator, iscsi_create_initiator, iscsi_delete_initiator, iscsi_display_auth_access_group_list, iscsi_create_auth_access_group, iscsi_view_auth_access_group, iscsi_delete_auth_access_group, iscsi_edit_auth_access_user, iscsi_edit_target_global_config, iscsi_view_target_global_config, iscsi_create_target,iscsi_view_target , iscsi_edit_target, iscsi_delete_target, iscsi_delete_auth_access_user, iscsi_create_auth_access_user
from integral_view.views.admin_auth  import login, logout, change_admin_password, configure_email_settings 
from integral_view.views.trusted_pool_setup  import add_nodes, remove_node
from integral_view.views.volume_creation import volume_creation_wizard, create_volume, create_volume_conf
from integral_view.views.volume_management import volume_specific_op , expand_volume, replace_node, set_volume_options, set_volume_quota, delete_volume, replace_disk, deactivate_snapshot, activate_snapshot, create_snapshot, delete_snapshot, restore_snapshot
from integral_view.views import perform_op
from integral_view.views.common import show, refresh_alerts, raise_alert, internal_audit, configure_ntp_settings, reset_to_factory_defaults, flag_node, hardware_scan 
from integral_view.views.log_management import download_vol_log, download_sys_log, rotate_log, view_rotated_log_list, view_rotated_log_file, edit_integral_view_log_level
#from integral_view.views.node_management import pull_node_status, node_status
#from integral_view.views.share_management import samba_server_settings_basic, save_samba_server_settings_basic, samba_server_settings_security, save_samba_server_settings_security, display_shares, create_share, view_samba_share, edit_samba_share, display_users, edit_samba_user, create_user, create_unix_user, samba_server_settings, save_samba_server_settings, samba_server_settings, view_share, edit_share
from integral_view.views.share_management import display_shares, create_share, samba_server_settings, save_samba_server_settings, view_share, edit_share, delete_share, edit_auth_method, view_local_users, create_local_user, change_local_user_password, delete_local_user
from django.contrib.auth.decorators import login_required
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'integral_view.views.home', name='home'),
    # url(r'^integral_view/', include('integral_view.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', login),
    url(r'^$', login),
    url(r'^raise_alert/', raise_alert),
    url(r'^flag_node/', flag_node),
    url(r'^internal_audit/', internal_audit),
    url(r'^change_admin_password/', login_required(change_admin_password),name="change_admin_password"),
    url(r'^create_snapshot/', login_required(create_snapshot)),
    url(r'^delete_snapshot/', login_required(delete_snapshot)),
    url(r'^restore_snapshot/', login_required(restore_snapshot)),
    url(r'^deactivate_snapshot/', login_required(deactivate_snapshot)),
    url(r'^activate_snapshot/', login_required(activate_snapshot)),
    url(r'^hardware_scan/', login_required(hardware_scan)),
    url(r'^configure_email_settings/', login_required(configure_email_settings)),
    url(r'^reset_to_factory_defaults/', login_required(reset_to_factory_defaults)),
    url(r'^configure_ntp_settings/', login_required(configure_ntp_settings)),
    url(r'^display_shares/', login_required(display_shares)),
    url(r'^view_local_users/', login_required(view_local_users)),
    url(r'^create_local_user/', login_required(create_local_user)),
    url(r'^delete_local_user/', login_required(delete_local_user)),
    url(r'^change_local_user_password/', login_required(change_local_user_password)),
    url(r'^create_share/', login_required(create_share)),
    url(r'^view_share/', login_required(view_share)),
    url(r'^edit_share/', login_required(edit_share)),
    url(r'^edit_auth_method/', login_required(edit_auth_method)),
    url(r'^delete_share/', login_required(delete_share)),
    url(r'^auth_server_settings/', login_required(samba_server_settings)),
    url(r'^save_samba_server_settings/', login_required(save_samba_server_settings)),
    url(r'^replace_node/', login_required(replace_node)),
    url(r'^replace_disk/', login_required(replace_disk)),
    url(r'^edit_integral_view_log_level/', login_required(edit_integral_view_log_level)),
    url(r'^set_volume_options/', login_required(set_volume_options)),
    url(r'^set_volume_quota/', login_required(set_volume_quota)),
    url(r'^remove_node/', login_required(remove_node)),
    url(r'^show/([A-Za-z0-9_]+)/([a-zA-Z0-9_\-\.]*)', login_required(show),name="show_page"),
    url(r'^refresh_alerts/([0-9_]*)', login_required(refresh_alerts)),
    url(r'^logout/', logout,name="logout"),
    url(r'^perform_op/([A-Za-z_]+)/([A-Za-z0-9_\-]*)/([A-Za-z0-9_\.\-\:\/]*)', login_required(perform_op.perform_op)),
    #url(r'^server_op/([A-Za-z_]+)', login_required(server_op)),
    url(r'^add_nodes/', login_required(add_nodes),name="add_nodes"),
    url(r'^volume_creation_wizard/([A-Za-z_]+)', login_required(volume_creation_wizard)),
    url(r'^create_volume/', login_required(create_volume)),
    url(r'^delete_volume/', login_required(delete_volume)),
    url(r'^create_volume_conf/', login_required(create_volume_conf)),
    url(r'^volume_specific_op/([A-Za-z_]+)/([A-Za-z0-9_\-]*)', login_required(volume_specific_op)),
    url(r'^expand_volume/', login_required(expand_volume)),
    url(r'^download_vol_log/', login_required(download_vol_log)),
    url(r'^download_sys_log/', login_required(download_sys_log)),
    url(r'^rotate_log/([A-Za-z_]+)', login_required(rotate_log)),
    url(r'^view_rotated_log_list/([A-Za-z_]+)', login_required(view_rotated_log_list)),
    url(r'^view_rotated_log_file/([A-Za-z_]+)', login_required(view_rotated_log_file)),
    url(r'^first_login/', login_required(hardware_scan)),
    #url(r'^sys_log/([A-Za-z]+)', sys_log),
    #url(r'^pull_node_status/([A-Za-z_\-0-9]+)', login_required(pull_node_status)),
    #url(r'^node_status/', node_status),
    ## url(r'^view_log/([A-Za-z_]*)/([0-9]*)/([0-9]*)', login_required(view_log)),
    ## url(r'^view_log/([A-Za-z_]*)', login_required(view_log)),
    #url(r'^download_vol_log/([A-Za-z0-9_\-\:\/]*)', login_required(download_vol_log)),
    #url(r'^display_users/', login_required(display_users)),
    #url(r'^create_user/', login_required(create_user)),
    #url(r'^create_unix_user/', login_required(create_unix_user)),
    #url(r'^perform_op/([A-Za-z_]+)/([A-Za-z0-9_\-]*)', login_required(perform_op.perform_op)),
    #url(r'^edit_samba_user/', login_required(edit_samba_user)),
    #url(r'^launch_swat/', login_required(launch_swat)),
    #url(r'^create_volume_get_num_bricks/([A-Za-z_]+)', login_required(get_num_bricks)),
    #url(r'^samba_server_settings_basic/', login_required(samba_server_settings_basic)),
    #url(r'^save_samba_server_settings_security/', login_required(save_samba_server_settings_security)),
    #url(r'^samba_server_settings_security/', login_required(samba_server_settings_security)),
    #url(r'^save_samba_server_settings_basic/', login_required(save_samba_server_settings_basic)),
    #url(r'^edit_samba_share/', login_required(edit_samba_share)),
    #url(r'^view_samba_share/', login_required(view_samba_share)),
)

'''
    url(r'^iscsi_display_targets/', login_required(iscsi_display_targets)),
    url(r'^iscsi_view_target/', login_required(iscsi_view_target)),
    url(r'^iscsi_create_target/', login_required(iscsi_create_target)),
    url(r'^iscsi_edit_target/', login_required(iscsi_edit_target)),
    url(r'^iscsi_delete_target/', login_required(iscsi_delete_target)),
    url(r'^iscsi_display_initiators/', login_required(iscsi_display_initiators)),
    url(r'^iscsi_view_initiator/', login_required(iscsi_view_initiator)),
    url(r'^iscsi_create_initiator/', login_required(iscsi_create_initiator)),
    url(r'^iscsi_delete_initiator/', login_required(iscsi_delete_initiator)),
    url(r'^iscsi_edit_initiator/', login_required(iscsi_edit_initiator)),
    url(r'^iscsi_display_auth_access_group_list/', login_required(iscsi_display_auth_access_group_list)),
    url(r'^iscsi_create_auth_access_group/', login_required(iscsi_create_auth_access_group)),
    url(r'^iscsi_create_auth_access_user/', login_required(iscsi_create_auth_access_user)),
    url(r'^iscsi_view_auth_access_group/', login_required(iscsi_view_auth_access_group)),
    url(r'^iscsi_delete_auth_access_group/', login_required(iscsi_delete_auth_access_group)),
    url(r'^iscsi_delete_auth_access_user/', login_required(iscsi_delete_auth_access_user)),
    url(r'^iscsi_edit_auth_access_user/', login_required(iscsi_edit_auth_access_user)),
    url(r'^iscsi_edit_target_global_config/', login_required(iscsi_edit_target_global_config)),
    url(r'^iscsi_view_target_global_config/', login_required(iscsi_view_target_global_config)),
'''
