#import abc

vals_cs_ug = [True, False]
vals_work_experience = range(0, 7)

# 0 = lowest, 4 = most
dict_coding_ability = range(0, 5)

vals_technical_strength = { 1 : "frontend",
							  	2 : "backend",
							  	3 : "UX",
							   	4 : "mobile",
							   	5 : "systems/hardware",
							   	6 : "databases",
								7 : "algorithms",
								8 : "graphics",
}

class StudentFieldError(Exception):
	def __init__(self, value):
		self.val = value
	def __str__(self):
		return repr(self.val)

class Student(object):

	#__metaclass__ = abc.ABCMeta

	global vals_cs_ug
	global vals_yrs_work_experience
	global dict_coding_ability
	global vals_technical_strength

	#@abc.abstractmethod

	# Defining checks and properties.
	def check_valid(self, val, lst, s=""):
		if (not (val in lst)):
		 	error = "Invalid input " + str(val) + " for student " + str(self._ID) + " for field" + s + "."
		 	raise StudentFieldError(error)
		else:
		 	pass

	def get_name(self):
		return self._name

	def set_name(self, val):
		self._name = val

	name = property(get_name, set_name, doc = "Get and set name.")

	def get_ID(self):
		return self._ID

	def set_ID(self, val):
		self._ID = val

	ID = property(get_ID, set_ID, doc = "Get and set student ID.")

	def get_coding_ability(self):
		return self._coding_ability

	def set_coding_ability(self, val):
		self.check_valid(val, dict_coding_ability, s = " coding ability")
		self._coding_ability = val

	coding_ability = property(get_coding_ability, set_coding_ability,
					 doc = "Get and set coding ability.")

	def get_cs_ug(self):
		return self._was_cs_ug

	def set_cs_ug(self, val):
		self.check_valid(val, vals_cs_ug, s = " was cs undergrad")
		self._was_cs_ug = val

	was_cs_ug = property(get_cs_ug, set_cs_ug,
				doc = "Get and set if student was a CS undergrad.")

	# TODO: should this be the int or the value?
	def get_technical_strength(self):
		return self._type_technical_strength

	def set_technical_strength(self, val):
		# Checks if the user is passing in the string value for technical strength.
		# If not, check if the int they're passing in is included in our dict.
		if (not(val in vals_technical_strength.values())):
			self.check_valid(val, vals_technical_strength, 
						s = " type of technical strength")
			self._type_technical_strength = vals_technical_strength[val]
		# If they are, set the technical strength
		else:
			self._type_technical_strength = val

	type_technical_strength = property(get_technical_strength, set_technical_strength,
						doc = "Get and set the type of the student's technical strength.")

	def get_work_experience(self):
		return self._work_experience

	def set_work_experience(self, val):
		self.check_valid(val, vals_work_experience, s = " num yrs. work experience")
		self._work_experience = val

	work_experience = property(get_work_experience, set_work_experience,
					  doc = "Get and set the num. yrs. of work experience.")

	def set_valid_properties(self, cod_abil, cs_ug, type_tech_stren, num_yrs_work_exp):
		
		self.set_coding_ability(cod_abil)
		self.set_cs_ug(cs_ug)
		self.set_technical_strength(type_tech_stren)
		self.set_work_experience(num_yrs_work_exp)

	def __init__ (self, name, ID, cod_abil, cs_ug, type_tech_stren, num_yrs_work_exp):
		''' 
			Parameters
			----------
			ca    = coding ability. Int from 0 to 4, inclusive.
			csug  = was cs undergrad. Boolean.
			tts   = type of technical strength. TechnicalStrength class/enum.
			nywe  = num. years of work experience. Int from 0 to 6 (6 = 6+).

		'''
		
		self._name				 	  = name
		self._ID				 	  = ID
		self.set_valid_properties(cod_abil, cs_ug, type_tech_stren, num_yrs_work_exp)
