
from fractalio import networking, command
import os, socket, sys


def display_status():

  try :
    hostname = socket.gethostname()
    if hostname and hostname in ['fractalio-pri', 'fractalio-sec']:
      print "DNS service status :"
      r, rc = command.execute_with_rc('service named status')
      l = command.get_output_list(r)
      if l:
        print '\n'.join(l)
      else:
        l = command.get_error_list(r)
        if l:
          print '\n'.join(l)
      print "Salt master service status :"
      r, rc = command.execute_with_rc('service salt-master status')
      l = command.get_output_list(r)
      if l:
        print '\n'.join(l)
      else:
        l = command.get_error_list(r)
        if l:
          print '\n'.join(l)
    print "Salt minion service status :",
    r, rc = command.execute_with_rc('service salt-minion status')
    l = command.get_output_list(r)
    if l:
      print '\n'.join(l)
    else:
      l = command.get_error_list(r)
      print l
      if l:
        print '\n'.join(l)
    print "Samba service status :",
    r, rc = command.execute_with_rc('service smb status')
    l = command.get_output_list(r)
    if l:
      print '\n'.join(l)
    else:
      l = command.get_error_list(r)
      if l:
        print '\n'.join(l)
    print "Winbind service status :",
    r, rc = command.execute_with_rc('service winbind status')
    l = command.get_output_list(r)
    if l:
      print '\n'.join(l)
    else:
      l = command.get_error_list(r)
      if l:
        print '\n'.join(l)
    print "CTDB service status :",
    r, rc = command.execute_with_rc('service ctdb status')
    l = command.get_output_list(r)
    if l:
      print '\n'.join(l)
    else:
      l = command.get_error_list(r)
      if l:
        print '\n'.join(l)
    print "Gluster service status :",
    r, rc = command.execute_with_rc('service glusterd status')
    l = command.get_output_list(r)
    if l:
      print '\n'.join(l)
    else:
      l = command.get_error_list(r)
      if l:
        print '\n'.join(l)
    print
    print "GRIDCell CTDB status :"
    r, rc = command.execute_with_rc('ctdb status')
    l = command.get_output_list(r)
    if l:
      print '\n'.join(l)
    else:
      l = command.get_error_list(r)
      if l:
        print '\n'.join(l)
  except Exception, e:
    print "Error displaying system status : %s"%e
    return -1
  else:
    return 0

if __name__ == '__main__':

  os.system('clear')
  print
  print
  print
  print "GRIDCell status"
  print "---------------"
  rc = display_status()
  print
  print
  #sys.exit(rc)

