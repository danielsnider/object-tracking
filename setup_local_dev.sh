#!/bin/bash
#
# Usage: sudo $1

# Add each project to your "/usr/lib/python2.7/sitecustomize.py" like so:

cat << EOF >> /usr/lib/python2.7/sitecustomize.py
import sys
sys.path.append('/home/ubuntu/pt/pt-pt')
sys.path.append('/home/ubuntu/pt/pt-client')
sys.path.append('/home/ubuntu/pt/pt-cookbook')
sys.path.append('/home/ubuntu/pt/pt-cv')
sys.path.append('/home/ubuntu/pt/pt-freight')
sys.path.append('/home/ubuntu/pt/pt-server')
sys.path.append('/home/ubuntu/pt/pt-website')
sys.path.append('/home/ubuntu/pt/pt-zklib')
sys.path.append('/usr/local/lib/python2.7/site-packages')
EOF

