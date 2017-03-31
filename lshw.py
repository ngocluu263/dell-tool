#!/usr/bin/python -tt
# Parse lshw output and collect hardware data.

# Code is taken from https://gist.github.com/amitsaha/4554484
# I need to modify and pick various other part such as cpu, memory.


from lxml import etree
from subprocess import Popen, PIPE

inventory = Popen(['lshw', '-xml', '-numeric'], stdout=PIPE).communicate()[0]
inventory = etree.XML(inventory)

find_disks = etree.XPath(".//node[@class='disk']")

numdisks = 0
diskspace = 0
for disk in find_disks(inventory):
    # has to be a hard-disk
    if disk.find('size') is not None:
        numdisks = numdisks + 1
        diskspace = diskspace + int(disk.find('size').text)
        print disk.find('description').text, disk.find('product').text, disk.find('logicalname').text
        print 'Disk Space: ', disk.find('size').text
        print 'Sector size: ', disk.find('configuration/setting/[@id="sectorsize"]').get('value')
        print

print 'Num disks', numdisks
print 'Total disk space', diskspace / (1024 ** 2)

