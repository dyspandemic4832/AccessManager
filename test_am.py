import access_manager
import random

DEBUG = True

am = access_manager.AccessManager(DEBUG)

def rand_num():
  return random.randint(0, 999999999)

id_peter = rand_num()
id_hannah = rand_num()
id_gunther = rand_num()
id_john = rand_num()

user = {
  id_peter : "Peter",
  id_hannah : "Hannah",
  id_gunther : "Gunther",
  id_john : "John"
}

def test_groups():
  am.add_group("Owner")
  am.add_group("Admin")
  am.add_group("Moderator")
  am.add_group("Supporter")
  am.add_group("Member")

  # duplication test
  am.add_group("Owner")
  am.del_group("Supporter")
  am.del_group("Supporter")

  am.find_groups()

def test_users():
  # adding users
  for id in user.keys():
    am.add_user(id, user[id])

  # listing users
  am.find_users()

  # duplication test
  am.add_user(id_peter, "Peter")

  # deleting users
  am.del_user(rand_num()) # random id
  am.del_user(id_peter)   # Peter (R.I.P.)

def test_add_users_to_groups():

  if DEBUG:
    am.add_user_to_group(0, "Owner")
  
  am.add_user_to_group(id_peter, "Moderator")
  am.add_user_to_group(id_hannah, "Supporter")
  am.add_user_to_group(id_gunther, "Member")
  am.add_user_to_group(id_john, "Member") 

  # duplication test
  am.add_user_to_group(id_john, "Member")
  am.remove_user_from_group(id_john, "Member")
  am.remove_user_from_group(id_john, "Member")
  
test_users()
test_groups()
test_add_users_to_groups()