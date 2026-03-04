<img width="698" height="645" alt="image" src="https://github.com/user-attachments/assets/086428e3-1260-4e41-bdec-862c7a2e20cd" />

### Recovering a Deleted Flag from USB (Mirai Challenge)

> What is the name of the service running on TCP port 53 on Mirai? Don't include a version number.
> 

I use scanning for this questions 

```php
nmap -sV 10.129.95.1
```

<img width="1638" height="262" alt="image" src="https://github.com/user-attachments/assets/48547e05-2c53-4369-b8d7-32a39fc55388" />

> What unusual HTTP header is included in the response when visiting the service on port 80?
> 

```php
$ curl -I http://10.129.95.1
```

<img width="1616" height="165" alt="image" src="https://github.com/user-attachments/assets/7eb00a21-6feb-4fd9-a589-3c5800e40337" />

and right away yyou can see the http header

> What relative path on the webserver presents the Pi-hole dashboard?
> 

to answer this questions i use gobuster tool to identify it

<img width="1635" height="423" alt="image" src="https://github.com/user-attachments/assets/df97286b-f896-4d49-ab20-fda156758531" />

click th elink and it will bring you to dashboard section 

<img width="1492" height="618" alt="image" src="https://github.com/user-attachments/assets/8b5adde6-85d5-4b17-96bf-010c2006b828" />

so the answer is 

```php
/admin
```

> What was the default username on a Raspberry Pi device?
> 

> What is the default password for the pi user?
> 

just do some googling and you will get the answer 

<img width="1208" height="543" alt="image" src="https://github.com/user-attachments/assets/a09e3b5c-ce61-4285-9804-4ef3af708bed" />

> Submit the flag located on the pi user's desktop.
> 

So log in as SSH to catch the flag

<img width="1620" height="614" alt="image" src="https://github.com/user-attachments/assets/31023e14-8dd7-490c-8c80-11cef7d54b67" />

```php
ff837707441b257a20e32199d7c8838d
```

> Can the pi user run any command as root on Mirai?
> 

<img width="1207" height="28" alt="image" src="https://github.com/user-attachments/assets/d6b293a7-a5e2-443c-a066-89ad24386f28" />

the answer is yes

> The flag-less root.txt file mentions that it's on the USB stick. What is the mountpoint for a device that is labeled as a USB stick on this host?
> 

to confirm this just run `lsblk` command 

<img width="1598" height="132" alt="image" src="https://github.com/user-attachments/assets/71e1d624-4e4a-47f8-b10c-875b09fddc66" />

`/dev/sdb`

> When files are deleted from a drive, is the memory definitely immediately overwritten with something else?
> 

`no`

> Submit the flag located on the USB device.
> 

here come the tricky part i used another alternative way to get the flag 

```php
strings /dev/sdb > /tmp/usb_dump.txt
```

This command extracts all human-readable text from the raw USB device `/dev/sdb` and saves it into a file called `usb_dump.txt` inside the `/tmp` directory. It’s a common forensic technique used to recover deleted or hidden data—especially when files are no longer accessible through the filesystem. By scanning the raw device directly, it helps uncover remnants like filenames, flags, or messages that may still exist in unallocated space.

```php
less /tmp/usb_dump.txt
```

and read it right away 

<img width="1599" height="43" alt="image" src="https://github.com/user-attachments/assets/3891335a-4efd-45d9-88af-03802329eb4d" />

<img width="1620" height="365" alt="image" src="https://github.com/user-attachments/assets/421277f7-0cfb-4dda-a073-8ac987c29c85" />

and you can see the sha there and that is our flag
```php
3d3e483143ff12ec505d026fa13e020b```
