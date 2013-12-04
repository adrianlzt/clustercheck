clustercheck
============

Updated clustercheck, intended to be standalone service for the reporting of Percona XtraDB cluster nodes.

This module requires MySQLdb package for python to function, aswell as a present ~/.my.cnf for the use the service will run as.

This version is rewritten to use Python twisted, so this module is required.

To start at run time:
echo "/usr/bin/pyclustercheck -f /etc/my.cnf > /dev/null 2>&1 &" >> /etc/rc.local

Contribute
==========

1. fork it.
2. Create a branch (`git checkout -b my_markup`)
3. Commit your changes (`git commit -am "I made these changes 123"`) updating AUTHORS.txt
4. Push to the branch (`git push origin my_markup`)
5. Create an [Issue][1] with a link to your branch

[1]: https://github.com/Oneiroi/clustercheck/issues

