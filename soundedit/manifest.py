
import json
import os

from typing import Tuple

class Manifest:
	
	def __init__(self, file: str):
		self.manifest = file
		self.nodes = {}
		self._load_manifest()


	def _load_manifest(self):
		try:
			with open(self.manifest, 'r') as fp:
				self.nodes = json.load(fp)
		except Exception as e:
			print(f'Failed to load node manifest: {e}')


	def get_node_types(self) -> dict:
		return self.nodes


				
GAMES = {
	'chaos': Manifest(os.path.dirname(__file__) + '/games/chaos.json')
}
current = GAMES['chaos']
	
@staticmethod
def set_current(name: str):
	global current
	current = GAMES[name]

	
@staticmethod
def get_current() -> Manifest:
	global current
	return current


def color_for_type(type: str) -> Tuple[int, int, int]:
	match type:
		case 'vec3':
			return (0, 255, 0)
		case 'float':
			return (255, 255, 0)
		case 'speakers':
			return (255, 0, 0)
		case 'vec3x8':
			return (255, 0, 255)
		case _:
			raise Exception('Invalid type name')