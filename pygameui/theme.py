from itertools import chain
import resource

class Theme(object):
	def __init__(self):
		self._styles = {}

	def set(self, class_name, state, key, value):
		self._styles.setdefault(class_name, {}).setdefault(state, {})
		self._styles[class_name][state][key] = value

	def get_dict_for_class(self, class_name, state=None, base_name='View'):
		classes = []
		klass = class_name

		while True:
			classes.append(klass)
			if klass.__name__ == base_name:
				break
			klass = klass.__bases__[0]

		if state is None:
			state = 'normal'

		style = {}

		for klass in classes:
			class_name = klass.__name__

			try:
				state_styles = self._styles[class_name][state]
			except KeyError:
				state_styles = {}

			if state != 'normal':
				try:
					normal_styles = self._styles[class_name]['normal']
				except KeyError:
					normal_styles = {}

				state_styles = dict(chain(normal_styles.iteritems(),
										  state_styles.iteritems()))

			style = dict(chain(state_styles.iteritems(),
							   style.iteritems()))

		return style

	def get_dict(self, obj, state=None, base_name='View'):
		return self.get_dict_for_class(class_name=obj.__class__,
									   state=obj.state,
									   base_name=base_name)

	def get_value(self, class_name, attr, default_value=None,
				  state='normal', base_name='View'):
		styles = self.get_dict_for_class(class_name, state, base_name)
		try:
			return styles[attr]
		except KeyError:
			return default_value

current = None
