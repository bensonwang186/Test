sc failure "PowerPanel Personal Service" reset= 600 actions= restart/30000/restart/30000/restart/30000
sc config "PowerPanel Personal Service" depend= "RpcSs"