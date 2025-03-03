import logging
logger = logging.getLogger(__name__)

class Group:
  def __init__(self, g_name):
    self.name = g_name
    self.hierarchy = 0
    self.members = {}
    self.permissions = {
      "start" : False,
      "stop" : False,
      "restart" : False,
      "grant" : False
    }
    self.included_vm = {}
    self.excluded_vm = {}
    
  def add_user(self, id, u_name):
    if id not in self.members:
      self.members[id] = u_name
      return True
    return False

  def remove_user(self, id):
    if id in self.members:
      self.members.pop(id)
      return True
    return False
     
class User:
  def __init__(self, id, u_name):
    self.id = id
    self.name = u_name
    self.permissions = {
      "start" : False,
      "stop" : False,
      "restart" : False,
      "grant" : False
    }
    # "grant" for user is admin permission
    self.included_vm = {} # {id: name}
    self.excluded_vm = {} # {id: name}

  def add_vm(self, vmid:int, vmname:str, exclude:bool = False):
    if exclude:
      if vmid in self.included_vm:
        self.included_vm.pop(vmid)
        warn_msg = vmname + " was removed from included VMs"
        logger.warning(warn_msg)
      if vmid not in self.excluded_vm:
        self.excluded_vm[vmid] = vmname
        inf_msg = vmname + " was added to excluded VMs"
        logger.info(inf_msg)
      return True
    elif not exclude:
      if vmid in self.excluded_vm:
        self.excluded_vm.pop(vmid)
        warn_msg = vmname + " was removed from excluded VMs"
        logger.warning(warn_msg)
      if vmid not in self.included_vm:
        self.included_vm[vmid] = vmname
        inf_msg = vmname + " was added to included VMs"
        logger.info(inf_msg)
      return True
    else:
      err_msg = "VM ID (" + str(vmid) + ")is not valid"
      logger.error(err_msg)
      return False
      
class AccessManager:
  def __init__(self, debug:bool = False):
    self.users = {}
    self.groups = []
    # Need logic for importing User and Groups from a MySQL/MariaDB Database
    # Aswell as an option to safe it to the database

    if debug:
      log_level = logging.DEBUG
    else:
      log_level = logging.INFO

    logging.basicConfig(format='[%(asctime)s]: %(name)s: %(levelname)s: %(message)s', datefmt='%Y.%m.%d|%H:%M:%S', level=log_level)
    logger.info("Access Manager was initialized")
    if debug:
      self.debug()
      
  def debug(self):
    debug_msg = """
Root user was created
This user has all permissions
This user can grant permissions to other users
This is for testing purposes only"""

    logger.debug(debug_msg)
    self.add_user(0, "root")
    if self.find_users(0):
      for permission in self.users[0].permissions.keys():
        self.users[0].permissions[permission] = True

  def find_users(self, find = None):
    if find in self.users:
        return True
    elif find is None:
      info_msg = "Listing all users:"
      for id in self.users.keys():
        info_msg += "\n"
        info_msg += self.users[id].name
      logger.info(info_msg)
    else:
      err_msg = "No user was found"
      logger.error(err_msg)
    return False

  def find_groups(self, find = None):
    info_msg = ""
    if not find:
      info_msg = "Listing all groups:"
    if len(self.groups) > 0:
      for group in self.groups:
        info_msg += "\n"
        if not find:
          info_msg += group.name + "(" + str(group.hierarchy) + ")"
        elif group.name == find:
          debug_msg = group.name + " was found"
          logger.debug(debug_msg)
          return True
      logger.info(info_msg)
    else:
      err_msg = "No Group was found"
      logger.error(err_msg)
      return False

  def sort_groups(self):
    if len(self.groups) > 1:
      existing_hierarchies = sorted(set(group.hierarchy for group in self.groups))
      hierarchy_map = {old: new for new, old in enumerate(existing_hierarchies)}
      for group in self.groups:
        group.hierarchy = hierarchy_map[group.hierarchy]
      self.groups.sort(key=lambda g: g.hierarchy)
      debug_msg = "Sorted groups"
      logger.debug(debug_msg)
      return True
    else:
      return False
    
  def allocate_group(self, g_name, pos:int):
    group_to_move = next((g for g in self.groups if g.name == g_name), None)
    if not group_to_move:
      err_msg = "Group " + g_name + " does not exist."
      logger.error(err_msg)
      return False
    
    old_pos = group_to_move.hierarchy
    if old_pos == pos:
      warn_msg = "Group " + g_name + " is already at position " + str(pos) + "."
      logger.warning(warn_msg)
      return False
    
    for group in self.groups:
      if old_pos < pos and old_pos < group.hierarchy <= pos:
        group.hierarchy -= 1
      elif old_pos > pos and pos <= group.hierarchy < old_pos:
        group.hierarchy += 1
    
    group_to_move.hierarchy = pos
    self.sort_groups()
    inf_msg = "Moved group " + g_name + " to position " + str(pos) + " and updated others accordingly."
    logger.info(inf_msg)
    return True
  
  def add_user(self, id, u_name):
    if id in self.users:
      err_msg = self.users[id].name + "(" + str(id) + ") does already exist"
      logger.error(err_msg)
      return False
      
    new_user = User(id, u_name)
    
    self.users[id] = new_user
    inf_msg = new_user.name + "(" + str(id) + ") was added"
    logger.info(inf_msg)
    return True
    
  def del_user(self, id, validator = None):
    if id in self.users:
      u_name = self.users[id].name
      del self.users[id]
      inf_msg = u_name + " was removed"
      logger.info(inf_msg)
      return True
    else:
      err_msg = "(" + str(id) + ") does not exist"
      logger.error(err_msg)
      return False
    
  def add_group(self, g_name, wish_pos:int = None):
    for group in self.groups:
      if group.name == g_name:
        err_msg = g_name + " does already exist"
        logger.info(err_msg)
        return False
    new_group = Group(g_name)
    new_group.hierarchy = len(self.groups)
    self.groups.append(new_group)
    if wish_pos:
      self.allocate_group(g_name, wish_pos)
    
    inf_msg = g_name + " was added on position: " + str(new_group.hierarchy)
    logger.info(inf_msg)
    return True
      
  def del_group(self, g_name, validator = None):
    for group in self.groups:
      if group.name == g_name:
        self.groups.remove(group)
        inf_msg = g_name + " was removed"
        logger.info(inf_msg)
        self.sort_groups()
        return True
    err_msg = g_name + " does not exist"
    logger.error(err_msg)
    return False

  def add_user_to_group(self, id, g_name):
    if self.find_users(id):
      for group in self.groups:
        if group.name == g_name:
          group.add_user(id, self.users[id].name)
          inf_msg = self.users[id].name + " was added to " + g_name
          logger.info(inf_msg)
          return True
      err_msg = g_name + " does not exist"
      logger.error(err_msg)
    else:
      err_msg = "(" + str(id) + ") does not exist"
      logger.error(err_msg)
    return False

  def remove_user_from_group(self, id, g_name):
    if self.find_users(id):
      if self.find_groups(g_name):
        for group in self.groups:
          if group.name == g_name:
            if group.remove_user(id):
              inf_msg = self.users[id].name + " was removed from " + g_name
              logger.info(inf_msg)
              return True
            else:
              err_msg = self.users[id].name + " is not a member of " + g_name
              logger.error(err_msg)
              return False
    return False
  
  # move function to class User
  def check_user_permission(self, id, command, vmid:int = None):
    if self.find_users(id):
      if command in self.users[id].permissions:
        if command == "grant":
          return self.users[id].permissions[command]
        elif vmid is not None and type(vmid) == int:
          if vmid in self.users[id].included_vm.keys() and vmid not in self.users[id].excluded_vm.keys():
            return self.users[id].permissions[command]
        else:
          return False
      else:
        err_msg = "Command does not exist"
        logger.error(err_msg)
        return False
    else:
      return False

  # move function to class Group  
  def check_group_permission(self, g_name, command:str, vmid:int = None):
    if self.find_groups(g_name):
      for group in self.groups:
        if group.name == g_name:
          if command in group.permissions:
            if command == "grant":
              return group.permissions[command]
            elif vmid is not None and type(vmid) == int:
              if vmid in group.included_vm.keys() and vmid not in group.excluded_vm.keys():
                return group.permissions[command]
              return True
            else:
              err_msg = "VM ID is not valid"
              logger.error(err_msg)
          else:
            err_msg = "Command does not exist"
            logger.error(err_msg)
    else:
      err_msg = "Group does not exist"
      logger.error(err_msg)
    return False
  
  def modify_user_permission(self, id, command:str, validator):
    if self.find_users(id):
      if command in self.users[id].permissions:
        if self.check_user_permission(validator, "grant"):
          if self.users[id].permissions[command]:
            self.users[id].permissions[command] = False
          elif not self.users[id].permissions[command]:
            self.users[id].permissions[command] = True
          return True
        else:
          err_msg = "Validator does not has the permission"
          logger.warning(err_msg)
      else:
        err_msg = "Command does not exist"
        logger.error(err_msg)
    return False
	
  def modify_group_permission(self, g_name, command:str, validator):
    pass