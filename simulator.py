import matplotlib.pyplot as plt
import math
import yaml
import pprint
import random
import csv
from tqdm import tqdm

class FrictionSimulationEnginer:
	'''
	This is the main class for friction simulation.
	'''
	def __init__(self, materialCoeffMapping, materialDensityMapping,
				 materialColorMapping, envGMapping, envColorMapping):
		'''
		materialCoeffMapping: 
			Description:
				The friction coefficient of included 
				material (the slope) types.
				{material_name : coefficent}
		materialDensityMapping: 
			Description:
				The density of included materialis 
				for blocks. Unit is [missing]
				{material_name : density}
		materialColorMapping: 
			Description:
				The color of included materialis.
				{material_name : color}
		envGMapping: 
			Description:
				The gravity accelerations for different enviroment.
				The default should be 9.81 which is on earth.
				{env_name : gravity acceleration}
		envColorMapping: 
			Description:
				The color for different enviroment.
				{env_name : color}
		'''
		self.materialCoeffMapping = materialCoeffMapping
		self.materialDensityMapping = materialDensityMapping
		self.materialColorMapping = materialColorMapping
		self.envGMapping = envGMapping
		self.envColorMapping = envColorMapping

	def _drawTriangle(self, angle):
		'''
		Helper function to draw the slope, points are labeled like this.
		(1)
			|\
		    | \
		    |  \
		(0) ----- (2)
		'''
		# This is constant
		base_x_y = 1.0
		slope_length = 10

		angle_pi = (angle*0.5/90.0)*math.pi
		pivot_height = slope_length*math.sin(angle_pi)
		slope_width = slope_length*math.cos(angle_pi)
		
		point_base = [base_x_y,base_x_y]
		point_pivot = [base_x_y,base_x_y + pivot_height]
		point_slope = [base_x_y + slope_width,base_x_y]

		return [point_base, point_pivot, point_slope]

	def _drawBlock(self, tri, angle, b_width, b_height):
		'''
		Helper function to draw blocks, points are labeled like this.
		(1) ---------- (2)
		    |        |
		    |        |
		    |        |
		(0) ---------- (3)
		tri:
			Description:
				Drawing the block will need the position of the triangle to
				determine where to place the block
		material:
			Description:
				The material of the block
		'''
		base_point_x = tri[0][0] + (tri[2][0] - tri[0][0])*0.5
		base_point_y = tri[0][1] + (tri[1][1] - tri[0][1])*0.5
		angle_pi = (angle*0.5/90.0)*math.pi
		delta_y = (b_width*1.0/2)*math.sin(angle_pi)
		delta_x = (b_width*1.0/2)*math.cos(angle_pi)
		point0_x = base_point_x - delta_x
		point0_y = base_point_y + delta_y
		point3_x = base_point_x + delta_x
		point3_y = base_point_y - delta_y	

		big_delta_y = b_height*math.cos(angle_pi)
		big_delta_x	= b_height*math.sin(angle_pi)
		top_base_point_x = base_point_x + big_delta_x
		top_base_point_y = base_point_y + big_delta_y
		point1_x = top_base_point_x - delta_x
		point1_y = top_base_point_y + delta_y
		point2_x = top_base_point_x + delta_x
		point2_y = top_base_point_y - delta_y

		return [[point0_x,point0_y], [point1_x,point1_y],
				[point2_x,point2_y], [point3_x,point3_y]]

	def _draw(self, tri, rec, material, env,
			  stroke_size=5.0, show=False):
		'''
		'''
		slope_col = self.materialColorMapping[material["slope"]]
		block_col = self.materialColorMapping[material["block"]]
		env_col = self.envColorMapping[env]

		fig, ax = plt.subplots()
		# draw triangle
		plt.fill([tri[0][0],tri[1][0],tri[2][0],tri[0][0]],
				 [tri[0][1],tri[1][1],tri[2][1],tri[0][1]],
				 slope_col, linewidth=stroke_size)
		# draw block
		plt.fill([rec[0][0],rec[1][0],rec[2][0],rec[3][0],rec[0][0]],
				 [rec[0][1],rec[1][1],rec[2][1],rec[3][1],rec[0][1]],
				 block_col, linewidth=stroke_size)
		# set for figures
		plt.xlim((0,2+10.0))
		plt.ylim((0,2+10.0))
		plt.xticks([], [])
		plt.yticks([], [])
		plt.gca().set_aspect('equal', adjustable='box')
		plt.gca().set_facecolor(env_col)

		ax.spines['top'].set_visible(False)
		ax.spines['right'].set_visible(False)
		ax.spines['bottom'].set_visible(False)
		ax.spines['left'].set_visible(False)
		
		if show:
			plt.show()
		
		return plt

	def generateSample(self, material={"block":"wood", "slope":"wood"},
					   angle=30.0,
					   b_width=3.0, b_height=3.0,
					   env="earth",
					   show=False):
		tri = self._drawTriangle(angle=angle)
		# TODO: only 2d shape for now
		rec = self._drawBlock(tri, angle=angle,
							  b_width=b_width, b_height=b_height)
		return self._draw(tri, rec, env=env, material=material, show=show)

	def slipOrNot(self, slope_material, block_material, env,
				  angle, b_width, b_height, b_depth):
		'''
		return - True if slip, False if not.
		'''
		V = b_width * b_height * b_depth
		pho = self.materialDensityMapping[block_material]
		M = pho * V * self.envGMapping[env]
		angle_pi = (angle*0.5/90.0)*math.pi
		M_down = M * math.cos(angle_pi)
		M_slope = M * math.sin(angle_pi)
		friction = M_down * self.materialCoeffMapping[slope_material]
		return M_slope > friction


if __name__ == "__main__":
	pp = pprint.PrettyPrinter(indent=4)

	# Test code by loading dataset
	import argparse
	parser = argparse.ArgumentParser()
	args = parser.parse_args()

	print("Starting Simulations...")
	property_list = None
	with open("./physics.yaml") as file:
		# The FullLoader parameter handles the conversion from YAML
		# scalar values to Python the dictionary format
		property_list = yaml.load(file, Loader=yaml.FullLoader)
	
	print("\n===   Simulation  ===")
	print("Units")
	pp.pprint(property_list['units'])
	print("======================")

	materialCoeffMapping = property_list['materials']['friction_coeff']
	materialDensityMapping = property_list['materials']['density']
	materialColorMapping = property_list['materials']['color']
	envGMapping = property_list['environment']['gravity_accel']
	envColorMapping	= property_list['environment']['color']

	simulator = FrictionSimulationEnginer(materialCoeffMapping,
										  materialDensityMapping, 
										  materialColorMapping, 
										  envGMapping,
										  envColorMapping)

	B_DEPTH = 3
	SAMPLE_N = 1000
	ANGLE = [i*5 for i in range(1, 11)]
	DIM1 = [i for i in range(1,3)]
	DIM2 = [i for i in range(0,4)]
	labels = []
	headers = ["image", "label", "slope_material", "block_material",
			   "env", "angle", "b_width", "b_height", "b_depth"]
	rows = []
	for i in tqdm(range(SAMPLE_N)):
		# random select
		slope_material = random.choice(list(materialCoeffMapping.keys()))
		block_material = random.choice(list(materialDensityMapping.keys()))
		env = random.choice(list(envGMapping.keys()))
		angle = random.choice(ANGLE)
		b_width = random.choice(DIM1) + random.choice(DIM2)
		b_height = random.choice(DIM1)
		b_depth = B_DEPTH
		# calculate whether slip
		label = simulator.slipOrNot(slope_material, block_material, env,
									angle, b_width, b_height, b_depth)
		labels.append(label)
		# print(label)
		sample = simulator.generateSample(
							material={
								"block":block_material,
								"slope":slope_material},
							angle=angle,
							b_width=b_width, b_height=b_height,
							env=env,
							show=False)
		output_name = "_".join(["ID", str(i), str(label)[0]])
		sample.savefig('./samples/' + output_name + '.png')
		row = [output_name, str(label), slope_material, block_material,
			   env, str(angle), str(b_width), str(b_height), str(b_depth)]
		rows.append(row)
	print("Wiriting metadata to a file...")
	# write metadata as well
	with open('./samples/metadata.csv', mode='w') as _file:
		_file_w = csv.writer(_file, delimiter=',')
		_file_w.writerow(headers)
		for row in rows:
			_file_w.writerow(row)
