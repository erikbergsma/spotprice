#Spotprice

**tl;dr**:
these tools allow for spawning and automatic re-spawning of spot instances.

**long**:
### Spot instances: unreliable but cheap
Using spot instances is great because they can be 3 to 4 times less expensive compared to on demand instances
more info can be found here: http://aws.amazon.com/ec2/purchasing-options/spot-instances/

By design spot instances can be gone at any given second they, due to a raised average price
Therefore making spot instances far from ideal in a high available (HA) setup, which is dissapointing because it can be a huge cost saver.

### There is got to be better way!
However spot instances can still be used for redundant copies of servers in your HA setup:
for example: you have a small HA setup, 1 ELB and 2 webservers (web1, web2) in 2 availability zones
if one of these webservers (web2) dies, your website is still up and running, due to web1 still beeing there.
So if we are ok with one of the webservers dying, we may as well use a spot instance for this!

Availability of your website is still guranteed by the other redundant copy of the server (web1)
and therefore we highly recommend using a on demand / reserved instance for this server.

### Core problem and solution
The problem here is that as soon as web2 dies, we are stuck with a SPOF (single point of failure) in your HA design; if web1 does your website is down.
Since AWS does not support dynamic spawning / pricing of spot instances, we have decided to build a tool that does that our selves.

In practical sence this means that after you spawned your server, the details of your server are stored in zookeeper.
Next step is that every X minutes there is a daemon checking if your spot instance is still up and running, and if not, it relaunches it.
This limits the time that you are stuck with a SPOF to about 5-10 minutes. Which is on our eyes acceptable compared to the amount of cost savings.

### About the price
Its hard to determine a "safe enough" price for your spot instance; if the price is too low your instance may be killed too quickly,
if it is too high you are paying to much (while the idea is cost saving) 

However since a replacing spot instance can be spawned in a matter of minutes we have decided to bid as low as possible, and maximize cost savings.
this means that the script gets the current bidprice for your ec2 region, and adds 1% 

this value of 1% can be overridden while using new_instance.py

## Requirements:
- a working (non encrypted / authenticated) zookeeper cluster
- kazoo installed
- boto installed
- a copy of the code in this repo

## How to:
1. copy and modify spotprice.cfg and store it on /root/ or your current workdir on your system / server
2. start a new instance by new_instance.py (use the --help!!!)
3. set a cron somewhere on a server for check_running_instances.py (recommended setting is every 5 minutes)

