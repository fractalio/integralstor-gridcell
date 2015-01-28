
import django, django.template

import integral_view
from integral_view.forms import samba_shares_forms
from integral_view.samba import samba_settings, local_users

import fractalio
from fractalio import volume_info, system_info, audit

def display_shares(request):

  return_dict = {}
  template = 'logged_in_error.html'
  try :
    shares_list = samba_settings.load_shares_list()
  except Exception, e:
    return_dict["error"] = "Error loading share information - %s" %e

  if not "error" in return_dict:
    if "action" in request.GET:
      if request.GET["action"] == "saved":
        conf = "Share information successfully updated"
      elif request.GET["action"] == "created":
        conf = "Share successfully created"
      elif request.GET["action"] == "deleted":
        conf = "Share successfully delete"
      return_dict["conf"] = conf
    return_dict["shares_list"] = shares_list
    template = "view_shares_list.html"
  return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))


def view_share(request):

  return_dict = {}
  template = 'logged_in_error.html'

  if request.method != "GET":
    return_dict["error"] = "Incorrect access method. Please use the menus"

  if "index" not in request.GET or "access_mode" not in request.GET:
    return_dict["error"] = "Unknown share"

  if not "error" in return_dict:

    access_mode = request.GET["access_mode"]
    index = request.GET["index"]

    if "action" in request.GET and request.GET["action"] == "saved":
      return_dict["conf_message"] = "Information updated successfully"

    valid_users_list = None
    try:
      share = samba_settings.load_share_info(access_mode, index)
      valid_users_list = samba_settings.load_valid_users_list(share["share_id"])
    except Exception, e:
      return_dict["error"] = "Error retrieving share information - %s" %e
    else:
      if not share:
        return_dict["error"] = "Error retrieving share information for  %s" %share_name
      else:
        return_dict["share"] = share
        if valid_users_list:
          return_dict["valid_users_list"] = valid_users_list
        template = 'view_share.html'

  return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))

def edit_share(request):

  return_dict = {}
  vil = volume_info.get_volume_info_all()
  user_list = samba_settings.get_user_list()
  group_list = samba_settings.get_group_list()

  if request.method == "GET":
    # Shd be an edit request
    if "share_id" not in request.GET:
      return_dict["error"] = "Unknown share specified"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    share_id = request.GET["share_id"]
    try :
      share_dict = samba_settings.load_share_info("by_id", share_id)
      valid_users_list = samba_settings.load_valid_users_list(share_dict["share_id"])
    except Exception, e:
      return_dict["error"] = "Error loading share information - %s" %e
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

    # Set initial form values
    initial = {}
    initial["share_id"] = share_dict["share_id"]
    initial["name"] = share_dict["name"]
    initial["path"] = share_dict["path"]
    initial["display_path"] = share_dict["display_path"]
    initial["vol"] = share_dict["vol"]
    if share_dict["guest_ok"]:
      initial["guest_ok"] = True
    else:
      initial["guest_ok"] = False
    if share_dict["browseable"]:
      initial["browseable"] = True
    else:
      initial["browseable"] = False
    if share_dict["read_only"]:
      initial["read_only"] = True
    else:
      initial["read_only"] = False
    initial["comment"] = share_dict["comment"]

    if valid_users_list:
      vgl = []
      vul = []
      for u in valid_users_list:
        if u["grp"]:
          vgl.append(u["name"])
        else:
          vul.append(u["name"])
      initial["users"] = vul
      initial["groups"] = vgl

    form = samba_shares_forms.ShareForm(initial = initial, user_list = user_list, group_list = group_list, volume_list = vil)

    return_dict["form"] = form
    return django.shortcuts.render_to_response('edit_share.html', return_dict, context_instance=django.template.context.RequestContext(request))

  else:

    # Shd be an save request
    form = samba_shares_forms.ShareForm(request.POST, user_list = user_list, group_list = group_list, volume_list = vil)
    return_dict["form"] = form
    if form.is_valid():
      cd = form.cleaned_data
      try :
        name = cd["name"]
        share_id = cd["share_id"]
        path = cd["path"]
        if "comment" in cd:
          comment = cd["comment"]
        else:
          comment = None
        if "read_only" in cd:
          read_only = cd["read_only"]
        else:
          read_only = False
        if "browseable" in cd:
          browseable = cd["browseable"]
        else:
          browseable = False
        if "guest_ok" in cd:
          guest_ok = cd["guest_ok"]
        else:
          guest_ok = False
        if "users" in cd:
          users = cd["users"]
        else:
          users = None
        if "groups" in cd:
          groups = cd["groups"]
        else:
          groups = None
        vol = cd["vol"]
        #logger.debug("Save share request, name %s path %s, comment %s, read_only %s, browseable %s, guest_ok %s, users %s, groups %s, vol %s"%(name, path, comment, read_only, browseable, guest_ok, users, groups))
        samba_settings.save_share(share_id, name, comment, guest_ok, read_only, path, browseable, users, groups, vol)
        samba_settings.generate_smb_conf()
      except Exception, e:
        return_dict["error"] = "Error saving share information - %s" %e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

      audit_str = "Modified share %s"%cd["name"]
      audit.audit("modify_share", audit_str, request.META["REMOTE_ADDR"])

      return django.http.HttpResponseRedirect('/view_share?access_mode=by_id&index=%s&action=saved'%cd["share_id"])

    else:
      #Invalid form
      return django.shortcuts.render_to_response('edit_share.html', return_dict, context_instance=django.template.context.RequestContext(request))

def delete_share(request):

  return_dict = {}
  if request.method == "GET":
    #Return the conf page
    share_id = request.GET["share_id"]
    name = request.GET["name"]
    return_dict["share_id"] = share_id
    return_dict["name"] = name
    return django.shortcuts.render_to_response("delete_share_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
  else:
    share_id = request.POST["share_id"]
    name = request.POST["name"]
    #logger.debug("Delete share request for name %s"%name)
    try :
      samba_settings.delete_share(share_id)
      samba_settings.generate_smb_conf()
    except Exception, e:
      return_dict["error"] = "Error deleting share - %s" %e
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

    audit_str = "Deleted Samba share %s"%name
    audit.audit("delete_share", audit_str, request.META["REMOTE_ADDR"])
    return django.http.HttpResponseRedirect('/display_shares?action=deleted')


def create_share(request):

  user_list = samba_settings.get_user_list()
  group_list = samba_settings.get_group_list()
  vil = volume_info.get_volume_info_all()

  if request.method == "GET":
    #Return the form
    return_dict = {}
    form = samba_shares_forms.ShareForm(user_list = user_list, group_list = group_list, volume_list = vil)
    return_dict["form"] = form
    return django.shortcuts.render_to_response("create_share.html", return_dict, context_instance = django.template.context.RequestContext(request))
  else:
    #Form submission so create
    return_dict = {}
    form = samba_shares_forms.ShareForm(request.POST, user_list = user_list, group_list = group_list, volume_list = vil)
    return_dict["form"] = form
    if form.is_valid():
      cd = form.cleaned_data
      name = cd["name"]
      path = "%s"%cd["path"]
      display_path = cd["path"]
      if "comment" in cd:
        comment = cd["comment"]
      else:
        comment = None
      if "read_only" in cd:
        read_only = cd["read_only"]
      else:
        read_only = None
      if "browseable" in cd:
        browseable = cd["browseable"]
      else:
        browseable = None
      if "guest_ok" in cd:
        guest_ok = cd["guest_ok"]
      else:
        guest_ok = None
      if "users" in cd:
        users = cd["users"]
      else:
        users = None
      if "groups" in cd:
        groups = cd["groups"]
      else:
        groups = None
      vol = cd["vol"]
      #logger.debug("Create share request, name %s path %s, comment %s, read_only %s, browseable %s, guest_ok %s, users %s, groups %s, vol %s"%(name, path, comment, read_only, browseable, guest_ok, users, groups))
      #path = "/%s%s"%(vol, display_path)
      try :
        samba_settings.create_share(name, comment, guest_ok, read_only, path, display_path, browseable, users, groups, vol)
        samba_settings.generate_smb_conf()
      except Exception, e:
        return_dict["error"] = "Error creating share - %s" %e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

      audit_str = "Created Samba share %s"%name
      audit.audit("create_share", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/display_shares?action=created')
    else:
      return django.shortcuts.render_to_response("create_share.html", return_dict, context_instance = django.template.context.RequestContext(request))

def samba_server_settings(request):

  return_dict = {}
  try :
    d = samba_settings.load_auth_settings()
  except Exception, e:
    return_dict["error"] = "Error loading authentication configuration - %s" %e
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

  if "action" in request.REQUEST and request.REQUEST["action"] == "edit":
    ini = {}
    if d:    
      for k in d.keys():
        ini[k] = d[k] 
    if d and d["security"] == "ads":
      form = samba_shares_forms.AuthADSettingsForm(initial=ini)
    #elif d["security"] == "users":
    else:
      form = samba_shares_forms.AuthUsersSettingsForm(initial=ini)
    return_dict["form"] = form
    return django.shortcuts.render_to_response('edit_samba_server_settings.html', return_dict, context_instance=django.template.context.RequestContext(request))

  # Else a view request
  return_dict["samba_global_dict"] = d

  if "action" in request.REQUEST and request.REQUEST["action"] == "saved":
    return_dict["conf"] = "Information updated successfully"
  return django.shortcuts.render_to_response('view_samba_server_settings.html', return_dict, context_instance=django.template.context.RequestContext(request))

def edit_auth_method(request):
  return_dict = {}

  try :
    d = samba_settings.load_auth_settings()
  except Exception, e:
    return_dict["error"] = "Error loading authentication configuration - %s" %e
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  return_dict["samba_global_dict"] = d

  if request.method == "GET":
    return django.shortcuts.render_to_response('edit_auth_method.html', return_dict, context_instance=django.template.context.RequestContext(request))
  else:
    #Save request
    if "auth_method" not in request.POST:
      return_dict["error"] = "Please select an authentication method" 
      return django.shortcuts.render_to_response('edit_auth_method.html', return_dict, context_instance=django.template.context.RequestContext(request))
    security = request.POST["auth_method"]
    if security == d["security"]:
      return_dict["error"] = "Selected authentication method is the same as before." 
      return django.shortcuts.render_to_response('edit_auth_method.html', return_dict, context_instance=django.template.context.RequestContext(request))

    try:
      samba_settings.change_auth_method(security)
    except Exception, e:
      return_dict["error"] = "Error updating authentication method - %s" %e
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

  return django.http.HttpResponseRedirect('/auth_server_settings?action=edit')


def save_samba_server_settings(request):

  return_dict = {}
  if request.method != "POST":
    return_dict["error"] = "Invalid access method. Please try again using the menus"
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

  if "security" not in request.POST:
    return_dict["error"] = "Invalid security specification. Please try again using the menus"
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

  if request.POST["security"] == "ads":
    form = samba_shares_forms.AuthADSettingsForm(request.POST)
  elif request.POST["security"] == "users":
    form = samba_shares_forms.AuthUsersSettingsForm(request.POST)
  else:
    return_dict["error"] = "Invalid security specification. Please try again using the menus"
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

  return_dict["form"] = form
  return_dict["action"] = "edit"

  if form.is_valid():
    cd = form.cleaned_data

    try :
      samba_settings.save_auth_settings(cd)
    except Exception, e:
      return_dict["error"] = "Error saving authentication settings - %s" %e
    if not "error" in return_dict:
      try :
        samba_settings.generate_smb_conf()
      except Exception, e:
        return_dict["error"] = "Error generating file share authentication config file- %s" %e
    if not "error" in return_dict and cd["security"] == "ads":
      try :
        samba_settings.kinit("administrator", cd["password"], cd["realm"])
        #pass
      except Exception, e:
        return_dict["error"] = "Error generating kerberos ticket - %s" %e
    if not "error" in return_dict and cd["security"] == "ads":
      try :
        samba_settings.net_ads_join("administrator", cd["password"], cd["password_server"])
      except Exception, e:
        return_dict["error"] = "Error joining Active Directory - %s" %e
    if not "error" in return_dict and cd["security"] == "ads":
      try :
        samba_settings.generate_krb5_conf()
      except Exception, e:
        return_dict["error"] = "Error generating kerberos config file - %s" %e
    samba_settings.restart_samba_services()
    if "error" in return_dict:
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  else:
    return django.shortcuts.render_to_response('edit_samba_server_settings.html', return_dict, context_instance=django.template.context.RequestContext(request))

  audit_str = "Modified share authentication settings"
  audit.audit("modify_samba_settings", audit_str, request.META["REMOTE_ADDR"])
  return_dict["form"] = form
  return_dict["conf_message"] = "Information successfully updated"
  return django.http.HttpResponseRedirect('/auth_server_settings?action=saved')

def view_local_users(request):

  return_dict = {}
  try:
    user_list = local_users.get_local_users()
  except Exception, e:
    return_dict["error"] = "Error retrieving local users - %s" %e
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

  return_dict["user_list"] = user_list

  if "action" in request.GET:
    if request.GET["action"] == "saved":
      conf = "Local user password successfully updated"
    elif request.GET["action"] == "created":
      conf = "Local user successfully created"
    elif request.GET["action"] == "deleted":
      conf = "Local user successfully deleted"
    elif request.GET["action"] == "changed_password":
      conf = "Successfully update password"
    return_dict["conf"] = conf
    if "warnings" in request.GET:
      return_dict["warnings"] = request.GET["warnings"]

  return django.shortcuts.render_to_response('view_local_users.html', return_dict, context_instance=django.template.context.RequestContext(request))

def create_local_user(request):
  if request.method == "GET":
    #Return the form
    return_dict = {}
    form = samba_shares_forms.LocalUserForm()
    return_dict["form"] = form
    return django.shortcuts.render_to_response("create_local_user.html", return_dict, context_instance = django.template.context.RequestContext(request))
  else:
    #Form submission so create
    return_dict = {}
    form = samba_shares_forms.LocalUserForm(request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      try :
        ret = local_users.create_local_user(cd["userid"], cd["name"], cd["password"])
        audit_str = "Created a local user %s"%cd["userid"]
        audit.audit("create_local_user", audit_str, request.META["REMOTE_ADDR"])
        url = '/view_local_users?action=created'
        if ret:
          warnings = ','.join(ret)
          url = "%s&warnings=%s"%(url, warnings)
        return django.http.HttpResponseRedirect(url)
      except Exception, e:
        return_dict["error"] = "Error creating the local user - %s" %e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    else:
      return_dict["form"] = form
      return django.shortcuts.render_to_response("create_local_user.html", return_dict, context_instance = django.template.context.RequestContext(request))

def delete_local_user(request):

  if "userid" not in request.REQUEST:
    return_dict["error"] = "Invalid request. No user name specified."
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

  if request.method == "GET":
    #Return the form
    return_dict = {}
    return_dict["userid"] = request.GET["userid"]
    return django.shortcuts.render_to_response("delete_local_user_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
  else:
    #Form submission so create
    return_dict = {}
    try :
      ret = local_users.delete_local_user(request.POST["userid"])
      audit_str = "Deleted a local user %s"%request.POST["userid"]
      audit.audit("delete_local_user", audit_str, request.META["REMOTE_ADDR"])
      url = '/view_local_users?action=deleted'
      if ret:
        warnings = ','.join(ret)
        url = "%s&warnings=%s"%(url, warnings)
      return django.http.HttpResponseRedirect(url)
    except Exception, e:
      return_dict["error"] = "Error deleting the local user - %s" %e
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

def change_local_user_password(request):

  if request.method == "GET":
    #Return the form
    return_dict = {}
    if "userid" not in request.GET:
      return_dict["error"] = "Invalid request. No user name specified."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    d = {}
    d["userid"] = request.GET["userid"]
    form = samba_shares_forms.PasswordChangeForm(initial=d)
    return_dict["form"] = form
    return django.shortcuts.render_to_response("change_local_user_password.html", return_dict, context_instance = django.template.context.RequestContext(request))
  else:
    #Form submission so create
    return_dict = {}
    form = samba_shares_forms.PasswordChangeForm(request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      try :
        local_users.change_password(cd["userid"], cd["password"])
      except Exception, e:
        return_dict["error"] = "Error creating the local user - %s" %e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

      audit_str = "Changed password for local user %s"%cd["userid"]
      audit.audit("change_local_user_password", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_local_users?action=changed_password')
    else:
      return_dict["form"] = form
      return django.shortcuts.render_to_response("change_local_user_password.html", return_dict, context_instance = django.template.context.RequestContext(request))
