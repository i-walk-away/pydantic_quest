from pydantic import BaseModel


class UserProfile(BaseModel):
    pass

# INFORMATION FOR CONTRIBUTORS

# this script is what will be displayed
# to the user in the code editor by default in your lesson.
# the user will then build upon your starter script
# in order to complete the assignment

# it should give structure, but not implementation:
# try not to define any fields, unless you think that
# manually creating a BaseModel is unneccesary work
# within the scope of your lesson. for example,
# if your lesson is mostly focused on writing validators,
# you can define a model in its entirety, so that the user
# only has to write validators

# make sure that your test cases in `cases.yaml` use the exact names
# of the classes / functions as they're defined here in the starter script.
# (this UserProfile class can be fully accessed and instantiated within your test case scripts)

# NOTE: always import everything that is needed to complete
# the assignment. refrain from absolute imports
# example: if your lesson is about validators,
# import neccessary validators explicitly in your starter script

# don't worry if you think your starter script is bad or
# if you think it does not meet the recommendations provided
# in this commented block. i am happy to help making it better :)
# delete this commented block in your lesson starter.
