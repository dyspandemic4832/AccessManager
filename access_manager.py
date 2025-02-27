import random

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
    else:
      print(self.members[id] + "(" + str(id) + ") is already a Member of " + self.name)
     
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
    self.included_vm = {}
    self.excluded_vm = {}
      
class AccessManager:
  def __init__(self):
    self.users = {}
    self.groups = []
    # Need logic for importing User and Groups from a MySQL/MariaDB Database
    # Aswell as an option to safe it to the database

  def find_users(self, find = None):
    if not find:
      print("Listing all users:")
    if len(self.users) > 0:
      for id in self.users.keys():
        if not find:
          print(self.users[id].name)
        elif id == find:
          return True
    else:
      print("No user was found")
      return False

  def find_groups(self, find = None):
    if not find:
      print("Listing all groups:")
    if len(self.groups) > 0:
      for group in self.groups:
        if not find:
          print(group.name + "(" + str(group.hierarchy) + ")")
        elif group.name == find:
          return True
    else:
      print("No Group was found")
      return False

  def sort_groups(self):
    if len(self.groups) > 1:
      existing_hierarchies = sorted(set(group.hierarchy for group in self.groups))
      hierarchy_map = {old: new for new, old in enumerate(existing_hierarchies)}
      for group in self.groups:
        group.hierarchy = hierarchy_map[group.hierarchy]
      self.groups.sort(key=lambda g: g.hierarchy)
      print("Sorted groups")
      return True
    else:
      return False
    
  def allocate_group(self, g_name, pos):
    group_to_move = next((g for g in self.groups if g.name == g_name), None)
    if not group_to_move:
      print(f"Group {g_name} does not exist.")
      return False
    
    old_pos = group_to_move.hierarchy
    if old_pos == pos:
      print(f"Group {g_name} is already at position {pos}.")
      return False
    
    for group in self.groups:
      if old_pos < pos and old_pos < group.hierarchy <= pos:
        group.hierarchy -= 1
      elif old_pos > pos and pos <= group.hierarchy < old_pos:
        group.hierarchy += 1
    
    group_to_move.hierarchy = pos
    self.sort_groups()
    print(f"Moved group {g_name} to position {pos} and updated others accordingly.")
    return True
  
  def add_user(self, id, u_name):
    if id in self.users:
      print(self.users[id].name + "(" + str(id) + ") does already exist")
      return False
      
    new_user = User(id, u_name)
    
    self.users[id] = new_user
      
    print(self.users[id].name + "(" + str(id) + ") was added")
    return True
    
  def del_user(self, id, validator = None):
    if id in self.users:
      u_name = self.users[id].name
      del self.users[id]
      print(u_name + " was removed")
      return True
    print(str(id) + " does not exist")
    return False
    
  def add_group(self, g_name, wish_pos = None):
    for group in self.groups:
      if group.name == g_name:
        print(g_name + " does already exist")
        return False
    new_group = Group(g_name)
    new_group.hierarchy = len(self.groups)
    self.groups.append(new_group)
    if wish_pos:
      print(g_name + " was added")
      self.allocate_group(g_name, wish_pos)
    else:
      print(g_name + " was added on position: " + str(new_group.hierarchy))
    return True
      
  def del_group(self, g_name, validator = None):
    for group in self.groups:
      if group.name == g_name:
        self.groups.remove(group)
        print(g_name + " was removed")
        self.sort_groups()
        return True
    print(g_name + " does not exist")
    return False

  def add_user_to_group(self, id, g_name):
    if self.find_users(id):
      for group in self.groups:
        if group.name == g_name:
          group.add_user(id, self.users[id].name)
          print(self.users[id].name + " was added to " + g_name)
          return True
      print(g_name + " does not exist")
      return False
    else:
      print(str(id) + " does not exist")
      return False
    
  def check_user_permission(self, id, command, vmid = None):
    if self.find_users(id):
      if command in self.users[id].permissions:
        if command == "grant":
          return self.users[id].permissions["grant"]
        elif vmid is not None and type(vmid) == int:
          if vmid in self.users[id].included_vm.keys() or vmid not in self.users[id].excluded_vm.keys():
            return self.users[id].permissions[command]
        else:
          return False
      else:
        print("Command does not exist")
        return False
    else:
      return False
    
  def check_group_permission(self, g_name, command, vmid = None):
    pass
  def modify_user_permission(self, u_name, command, validator):
    pass
  def modify_group_permission(self, g_name, command, validator):
    pass

def rand_num():
  return random.randint(0, 999999999)

def test_am():
  # ignore this garbage
  am = AccessManager()
  print("This is a test of all functions")
  
  user = {
    rand_num() : "Peter",
    rand_num() : "Hannah",
    rand_num() : "Gunther",
    rand_num() : "John"
  }

  id_peter = 0
  
  for id in user.keys():
    am.add_user(id, user[id])
    if user[id] == "Peter":
      id_peter = id
  am.find_users()
  am.add_user(id_peter, user[id_peter])
  am.del_user(rand_num())
  
  am.find_groups()
  am.add_group("Owner")
  am.add_group("Supporter")
  am.add_group("Member")
  am.add_group("Moderator", 1)

  am.allocate_group("Member", 1)
  
  am.del_group("Supporter")
  am.del_group("test")
  am.find_groups()

  for id in user.keys():
    if user[id] == "Hannah":
      am.add_user_to_group(id, "Moderator")
      am.add_user_to_group(id, "Moderator")
    if user[id] == "Peter":
      am.add_user_to_group(id, "Owner")
    if user[id] == "Gunther":
      am.add_user_to_group(id, "Member")
    if user[id] == "John":
      am.add_user_to_group(id, "Member")

  vmid = 1
  am.users[id_peter].permissions["start"] = True
  am.users[id_peter].included_vm[vmid] = "VM1"
  value = am.check_user_permission(id_peter, "start", vmid)
  print(am.users[id_peter].name + " has the permission to start VM ID: (" + str(vmid) + "): " + str(value))
  # print(am.check_user_permission(rand_num(), "start"))

if __name__ == "__main__":
  test_am()