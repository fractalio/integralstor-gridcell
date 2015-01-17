
from fractalio import command, common
import subprocess

bin_path = common.get_bin_dir()

def display(line1, line2=None):
  clear()
  if not line1:
    return -1
  if not line2:
    subprocess.Popen(["%s/fpctl"%(bin_path), "move",  '0', '0'])
    subprocess.Popen(["%s/fpctl"%(bin_path), "print",  line1 ])
  else:
    #print "moving"
    subprocess.Popen(["%s/fpctl"%(bin_path), "move",  '0', '0'])
    #print "printing"
    subprocess.Popen(["%s/fpctl"%(bin_path), "print",  line1 ])
    #print "moving"
    subprocess.Popen(["%s/fpctl"%(bin_path), "move",  '0', '1'])
    #print "printing"
    subprocess.Popen(["%s/fpctl"%(bin_path), "print",  line2 ])

def clear():
  subprocess.Popen(["%s/fpctl"%(bin_path), "clear"])

def main():

  #display("Line1")
  #display("Disk Errors", "_E_|__|__|__|")
  display("Disk Errorssome", "abcdeabcdeabcdea")
  #clear()

if __name__ == "__main__":
  main()
