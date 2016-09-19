
import integralstor_common,time,os
from integralstor_common import audit, zfs,command
from integralstor_gridcell import iscsi_stgt
from integral_view.forms import iscsi_stgt_forms

import django, django.template

def view_iscsi_targets(request):

  return_dict = {}
  try:
    target_list, err = iscsi_stgt.get_targets()
    if err:
      raise Exception(err)
  
    return_dict["target_list"] = target_list
  
    if "ack" in request.GET:
      ack_message = ''
      if request.GET["ack"] == "created":
        ack_message = "ISCSI target successfully created"
      elif request.GET["ack"] == "target_deleted":
        ack_message = "ISCSI target successfully created"
      return_dict["ack_message"] = ack_message
  
    return django.shortcuts.render_to_response('view_iscsi_targets.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "shares_and_targets_base.html"
    return_dict["page_title"] = 'ISCSI targets'
    return_dict['tab'] = 'view_iscsi_targets_tab'
    return_dict["error"] = 'Error loading ISCSI targets'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
  
def view_iscsi_target(request):

  return_dict = {}
  try:
    if 'name' not in request.GET:
      raise Exception("Malformed request. Please use the menus.")

    target, err = iscsi_stgt.get_target(request.GET['name'])
    if err:
      raise Exception(err)

    if not target:
      raise Exception("Specified target not found. Please use the menus.")
      
    return_dict["target"] = target
    if "ack" in request.GET:
      ack_message = ''
      if request.GET["ack"] == "lun_created":
        ack_message = "ISCSI LUN successfully created"
      elif request.GET["ack"] == "added_acl":
        ack_message = "ISCSI target ACL successfully added"
      elif request.GET["ack"] == "removed_acl":
        ack_message = "ISCSI target ACL successfully removed"
      elif request.GET["ack"] == "lun_deleted":
        ack_message = "ISCSI LUN successfully deleted"
      elif request.GET["ack"] == "deleted":
        ack_message = "ISCSI target successfully deleted"
      elif request.GET["ack"] == "added_initiator_authentication":
        ack_message = "ISCSI initiator authentication successfully added"
      elif request.GET["ack"] == "added_target_authentication":
        ack_message = "ISCSI target authentication successfully added"
      elif request.GET["ack"] == "removed_initiator_authentication":
        ack_message = "ISCSI initiator authentication successfully removed"
      elif request.GET["ack"] == "removed_target_authentication":
        ack_message = "ISCSI target authentication successfully removed"
      return_dict["ack_message"] = ack_message
  
    return django.shortcuts.render_to_response('view_iscsi_target.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "shares_and_targets_base.html"
    return_dict["page_title"] = 'ISCSI target details'
    return_dict['tab'] = 'view_iscsi_targets_tab'
    return_dict["error"] = 'Error loading ISCSI target details'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_iscsi_target(request):
  return_dict = {}
  try:
    if request.method == "GET":
      #Return the form
      form = iscsi_stgt_forms.IscsiTargetForm()
      return_dict["form"] = form
      return django.shortcuts.render_to_response("create_iscsi_target.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      form = iscsi_stgt_forms.IscsiTargetForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        ret, err = iscsi_stgt.create_target(cd["name"])
        if not ret:
          if err:
            raise Exception(err)
          else:
            raise Exception("Unknown error.")
        audit_str = "Created an ISCSI target %s"%cd["name"]
        audit.audit("create_iscsi_target", audit_str, request.META)
        url = '/view_iscsi_targets?ack=created'
        return django.http.HttpResponseRedirect(url)
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("create_iscsi_target.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "shares_and_targets_base.html"
    return_dict["page_title"] = 'Create an ISCSI target'
    return_dict['tab'] = 'view_iscsi_targets_tab'
    return_dict["error"] = 'Error creating an ISCSI target'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_iscsi_target(request):
  return_dict = {}
  try:
    if 'target_name' not in request.REQUEST:
      raise Exception("Malformed request. No target specified. Please use the menus.")

    target_name = request.REQUEST['target_name']

    if request.method == "GET":
      return_dict["target_name"] = target_name
      return django.shortcuts.render_to_response("delete_iscsi_target_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      ret, err = iscsi_stgt.delete_target(target_name)
      if not ret:
        if err:
          raise Exception(err)
        else:
          raise Exception("Unknown error")
      audit_str = "Deleted ISCSI target %s"%target_name
      url = '/view_iscsi_targets?ack=target_deleted'
      audit.audit("delete_iscsi_target", audit_str, request.META)
      return django.http.HttpResponseRedirect(url)
  except Exception, e:
    return_dict['base_template'] = "shares_and_targets_base.html"
    return_dict["page_title"] = 'Remove an ISCSI targets'
    return_dict['tab'] = 'view_iscsi_targets_tab'
    return_dict["error"] = 'Error removing an ISCSI target'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_iscsi_lun(request):

  return_dict = {}

  try:
    if 'target_name' not in request.REQUEST:
      raise Exception("Malformed request. No target specified. Please use the menus.")
    target_name = request.REQUEST['target_name']
    zvols, err = zfs.get_all_zvols()
    if err:
      raise Exception(err)
    #if not zvols:
    #  raise Exception("There are no block device volumes created. Please create one first before adding a LUN.")
    if request.method == "GET":
      #Return the form
      initial = {}
      initial['target_name'] = target_name
      form = iscsi_stgt_forms.IscsiLunForm(initial = initial)
      return_dict["form"] = form
      return django.shortcuts.render_to_response("create_iscsi_lun.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      form = iscsi_stgt_forms.IscsiLunForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        # Create a zvol 
        cmd = 'zfs create -s -b 64K -V %s frzpool/%s'%(cd['lun_size'],cd['lun_name']) 
        ret,err = command.execute_with_rc(cmd = cmd, shell=True)
        time.sleep(20)
        ret, err = iscsi_stgt.create_lun(cd["target_name"],"/dev/frzpool/%s"%cd['lun_name'])
        if not ret:
          if err:
            raise Exception(err)
          else:
            raise Exception("Unknown error.")
        audit_str = "Created an ISCSI LUN in target %s with path %s"%(cd["target_name"], cd['lun_name'])
        audit.audit("create_iscsi_lun", audit_str, request.META)
        url = '/view_iscsi_target?name=%s&ack=lun_created'%target_name
        return django.http.HttpResponseRedirect(url)
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("create_iscsi_lun.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "shares_and_targets_base.html"
    return_dict["page_title"] = 'Create an ISCSI LUN'
    return_dict['tab'] = 'view_iscsi_targets_tab'
    return_dict["error"] = 'Error creating an ISCSI LUN'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_iscsi_lun(request):
  return_dict = {}
  try:
    if 'target_name' not in request.REQUEST:
      raise Exception("Malformed request. No target specified. Please use the menus.")
    if 'store' not in request.REQUEST:
      raise Exception("Malformed request. No LUN specified. Please use the menus.")

    store = request.REQUEST['store']
    target_name = request.REQUEST['target_name']
    print store,target_name

    if request.method == "GET":
      return_dict["target_name"] = target_name
      return_dict["store"] = store
      return django.shortcuts.render_to_response("delete_iscsi_lun_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      ret, err = iscsi_stgt.delete_lun(target_name, store)
      if not ret:
        if err:
          raise Exception(err)
        else:
          raise Exception("Unknown error.")
      audit_str = "Deleted ISCSI LUN %s from target %s"%(store, target_name)
      cmd = 'zfs destroy frzpool/%s'%(store.split("/")[-1]) 
      ret,err = command.execute_with_rc(cmd = cmd, shell=True)
      url = '/view_iscsi_target?name=%s&ack=lun_deleted'%target_name
      audit.audit("delete_iscsi_lun", audit_str, request.META)
      return django.http.HttpResponseRedirect(url)
  except Exception, e:
    return_dict['base_template'] = "shares_and_targets_base.html"
    return_dict["page_title"] = 'Remove an ISCSI LUN'
    return_dict['tab'] = 'view_iscsi_targets_tab'
    return_dict["error"] = 'Error removing an ISCSI LUN'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def add_iscsi_user_authentication(request):
  return_dict = {}
  try:
    if 'authentication_type' not in request.REQUEST:
      raise Exception("Malformed request. No user type specified. Please use the menus.")
    if 'target_name' not in request.REQUEST:
      raise Exception("Malformed request. No target specified. Please use the menus.")

    authentication_type = request.REQUEST['authentication_type']
    target_name = request.REQUEST['target_name']

    if authentication_type not in ['incoming', 'outgoing']:
      raise Exception("Invalid user type. Please use the menus.")


    if request.method == "GET":
      #Return the form
      initial = {}
      initial['authentication_type'] = authentication_type
      initial['target_name'] = target_name
      form = iscsi_stgt_forms.IscsiAuthenticationForm(initial = initial)
      return_dict["form"] = form
      return django.shortcuts.render_to_response("add_iscsi_target_user.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      form = iscsi_stgt_forms.IscsiAuthenticationForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        ret, err = iscsi_stgt.add_user_authentication(cd['target_name'], cd['authentication_type'], cd["username"], cd["password"])
        if not ret:
          if err:
            raise Exception(err)
          else:
            raise Exception("Error adding the ISCSI target user.")
        if cd['authentication_type'] == 'incoming':
          audit_str = "Added ISCSI initiator authentication user %s for target %s"%(cd["username"], cd['target_name'])
          url = '/view_iscsi_target?name=%s&ack=added_initiator_authentication'%target_name
        else:
          audit_str = "Added ISCSI target authentication user %s for target %s"%(cd["username"], cd['target_name'])
          url = '/view_iscsi_target?name=%s&ack=added_target_authentication'%target_name
        audit.audit("add_iscsi_target_authentication", audit_str, request.META)
        return django.http.HttpResponseRedirect(url)
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("add_iscsi_target_user.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "shares_and_targets_base.html"
    return_dict["page_title"] = 'Add ISCSI authentication user'
    return_dict['tab'] = 'view_iscsi_targets_tab'
    return_dict["error"] = 'Error adding ISCSI authentication user'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def remove_iscsi_user_authentication(request):
  return_dict = {}
  try:
    if 'authentication_type' not in request.REQUEST:
      raise Exception("Malformed request. No user type specified. Please use the menus.")
    if 'target_name' not in request.REQUEST:
      raise Exception("Malformed request. No target namespecified. Please use the menus.")
    if 'username' not in request.REQUEST:
      raise Exception("Malformed request. No user name specified. Please use the menus.")

    authentication_type = request.REQUEST['authentication_type']
    target_name = request.REQUEST['target_name']
    username = request.REQUEST['username']

    if authentication_type not in ['incoming', 'outgoing']:
      raise Exception("Invalid user type. Please use the menus.")


    if request.method == "GET":
      return_dict["target_name"] = target_name
      return_dict["username"] = username
      return_dict["authentication_type"] = authentication_type
      return django.shortcuts.render_to_response("remove_iscsi_user_auth_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      ret, err = iscsi_stgt.remove_user_authentication(target_name, username, authentication_type)
      if not ret:
        if err:
          raise Exception(err)
        else:
          raise Exception("Unknown error.")
      if authentication_type == 'incoming':
        audit_str = "Removed ISCSI initiator authentication user %s for target %s"%(username, target_name)
        url = '/view_iscsi_target?name=%s&ack=removed_initiator_authentication'%target_name
      else:
        audit_str = "Removed ISCSI target authentication user %s for target %s"%(username, target_name)
        url = '/view_iscsi_target?name=%s&ack=removed_target_authentication'%target_name
      audit.audit("remove_iscsi_target_authentication", audit_str, request.META)
      return django.http.HttpResponseRedirect(url)
  except Exception, e:
    return_dict['base_template'] = "shares_and_targets_base.html"
    return_dict["page_title"] = 'Remove ISCSI authentication user'
    return_dict['tab'] = 'view_iscsi_targets_tab'
    return_dict["error"] = 'Error removing ISCSI authentication user'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def add_iscsi_acl(request):
  return_dict = {}
  try:
    if 'target_name' not in request.REQUEST:
      raise Exception("Malformed request. No target specified. Please use the menus.")

    target_name = request.REQUEST['target_name']
    target, err = iscsi_stgt.get_target(target_name)
    if err:
      raise Exception(err)
    if not target:
      raise Exception('Specified target not found')

    if request.method == "GET":
      #Return the form
      initial = {}
      initial['target_name'] = target_name
      form = iscsi_stgt_forms.IscsiAclForm(initial = initial)
      return_dict["form"] = form
      return django.shortcuts.render_to_response("add_iscsi_acl.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      form = iscsi_stgt_forms.IscsiAclForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        ret, err = iscsi_stgt.add_acl(cd['target_name'], cd['acl'])
        if not ret:
          if err:
            raise Exception(err)
          else:
            raise Exception("Unknown error.")
        audit_str = "Added ISCSI ACL %s for target %s"%(cd["acl"], cd['target_name'])
        url = '/view_iscsi_target?name=%s&ack=added_acl'%target_name
        audit.audit("add_iscsi_acl", audit_str, request.META)
        return django.http.HttpResponseRedirect(url)
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("add_iscsi_acl.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "shares_and_targets_base.html"
    return_dict["page_title"] = 'Add ISCSI ACL'
    return_dict['tab'] = 'view_iscsi_targets_tab'
    return_dict["error"] = 'Error adding ISCSI ACL'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def remove_iscsi_acl(request):
  return_dict = {}
  try:
    if 'acl' not in request.REQUEST:
      raise Exception("Malformed request. No ACL specified. Please use the menus.")
    if 'target_name' not in request.REQUEST:
      raise Exception("Malformed request. No target specified. Please use the menus.")

    acl = request.REQUEST['acl']
    target_name = request.REQUEST['target_name']

    if request.method == "GET":
      return_dict["target_name"] = target_name
      return_dict["acl"] = acl
      return django.shortcuts.render_to_response("remove_iscsi_acl_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      ret, err = iscsi_stgt.remove_acl(target_name, acl)
      if not ret:
        if err:
          raise Exception(err)
        else:
          raise Exception("Unknown error.")
      audit_str = "Removed ISCSI ACL %s for target %s"%(acl, target_name)
      url = '/view_iscsi_target?name=%s&ack=removed_acl'%target_name
      audit.audit("remove_iscsi_acl", audit_str, request.META)
      return django.http.HttpResponseRedirect(url)
  except Exception, e:
    return_dict['base_template'] = "shares_and_targets_base.html"
    return_dict["page_title"] = 'Remove ISCSI ACL'
    return_dict['tab'] = 'view_iscsi_targets_tab'
    return_dict["error"] = 'error Removing ISCSI ACL'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
