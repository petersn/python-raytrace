#!/usr/bin/python

import math, random, time
import pygame
import numpy
from numpy import linalg, array

WIDTH, HEIGHT = 200, 200

def normalized(x):
	return x / linalg.norm(x)

class Ray:
	def __init__(self, origin, direction):
		self.origin, self.direction = origin, normalized(direction)

class Hit:
	def __init__(self, point, incoming, normal, reflection, travel, obj):
		self.point, self.incoming, self.normal, self.reflection, self.travel, self.obj = point, incoming, normal, reflection, travel, obj

class Light:
	def __init__(self, point, color):
		self.point, self.color = point, color

class Material:
	def __init__(self):
		# TODO: Make this actually do anything.
		pass

class Sphere:
	def __init__(self, material, center, radius):
		self.material, self.center, self.radius = material, center, radius

	def cast_test(self, ray):
		offset = self.center - ray.origin
		base_d = ray.direction.dot(offset)
		discriminant = base_d**2 - linalg.norm(offset)**2 + self.radius**2
		if discriminant < 0:
			return
		root = math.sqrt(discriminant)
		if base_d - root < 0:
			return
		hit = ray.origin + ray.direction * (base_d - root - 1e-2)
		normal = normalized(hit - self.center)
		reflection = normalized(ray.direction - (2 * normal.dot(ray.direction)) * normal)
		return Hit(hit, ray.direction, normal, reflection, base_d - root, self)

class Plane:
	def __init__(self, material, normal, height):
		self.material, self.normal, self.height = material, normal, height

	def cast_test(self, ray):
		origin_height = self.normal.dot(ray.origin) - self.height
		if origin_height < 0:
			return
		rate = -self.normal.dot(ray.direction)
		if rate <= 0:
			return
		approach_distance = origin_height / rate
		hit = ray.origin + ray.direction * approach_distance
		reflection = normalized(ray.direction - (2 * self.normal.dot(ray.direction)) * self.normal)
		return Hit(hit, ray.direction, self.normal, reflection, approach_distance, self)

class Scene:
	dof_x = 3
	dof_y = 3
	dof_passes = dof_x * dof_y

	def __init__(self):
		self.objects = []
		self.lights = []

	def cast_test(self, ray):
		best_travel = float("inf")
		best_hit = None
		for obj in self.objects:
			hit = obj.cast_test(ray)
			if hit and hit.travel < best_travel:
				best_travel = hit.travel
				best_hit = hit
		return best_hit

	def color_ray(self, ray, recursions=0):
		energy = array([0.0, 0.0, 0.0])
		hit = self.cast_test(ray)
		if not hit:
			return energy
		# Cast shadow rays to each light.
		for light in self.lights:
			to_light = light.point - hit.point
			shadow_ray = Ray(hit.point, to_light)
			shadow_hit = self.cast_test(shadow_ray)
			distance_to_light = linalg.norm(to_light)
			if (not shadow_hit) or shadow_hit.travel > distance_to_light:
				raw_energy = light.color / distance_to_light**2.0
				lambertian_coef = hit.normal.dot(shadow_ray.direction)
				phong_coef = max(0.0, hit.reflection.dot(shadow_ray.direction))**15.0
				energy += raw_energy * (lambertian_coef + phong_coef)
		# If we have recursions left do an ideal reflection.
		if recursions > 0:
			reflection_ray = Ray(hit.point, hit.reflection)
			energy += 0.8 * self.color_ray(reflection_ray, recursions-1)
		# If the object is the plane, load from the texture.
		if isinstance(hit.obj, Plane):
			tex_x, tex_y = int(hit.point[0] * 100) + texture_size[0]/2, int(hit.point[1] * 100) + texture_size[1]/2
			tex_x %= texture_size[0]
			tex_y %= texture_size[1]
			energy *= numpy.array(map(float, texture.get_at((tex_x, tex_y))[:3])) / 255.0
		return energy

	def render(self, surface):
		aspect_ratio = WIDTH / HEIGHT
		camera_origin = array([0.0, -5.0, 1.0])
		plane_height = 0.8
		pof_distance = 5.5
		aperture_size = 0.08 #0.05 #0.4
		for y in xrange(HEIGHT):
			pygame.draw.line(screen, (255, 0, 0), (0, y+1), (WIDTH-1, y+1))
			for x in xrange(WIDTH):
				energy = array([0.0, 0.0, 0.0])
				for dof_x in xrange(self.dof_x):
					for dof_y in xrange(self.dof_y):
						# The random.uniform is to add dither to hide the shifted copies of the image.
						x_offset = aperture_size * (dof_x - self.dof_x / 2.0) + random.uniform(-aperture_size, aperture_size) / self.dof_x
						y_offset = aperture_size * (dof_y - self.dof_y / 2.0) + random.uniform(-aperture_size, aperture_size) / self.dof_y
						ray_direction = array([
							aspect_ratio * ((x - WIDTH/2.0)/HEIGHT) * plane_height - x_offset / pof_distance,
							1,
							((HEIGHT/2.0 - y)/HEIGHT) * plane_height - y_offset / pof_distance,
						])
						ray = Ray(camera_origin + array([x_offset, 0, y_offset]), ray_direction)
						energy += self.color_ray(ray, 4)
				color = self.energy_to_color(energy)
				surface.set_at((x, y), color)
			pygame.display.update()

	def energy_to_color(self, energy):
		gain = 255.0 / self.dof_passes
		f = lambda x: int(max(0.0, min(255.0, x*gain)))
		return map(f, energy)

scene = Scene()
ground_mat = Material()
scene.objects.append(Sphere(ground_mat, array([0.0, 0.4, 1.0]), 0.8))
scene.objects.append(Sphere(ground_mat, array([0.9, -1.0, 0.6]), 0.4))
scene.objects.append(Sphere(ground_mat, array([-1.1, -0.5, 1.5]), 0.6))
scene.objects.append(Plane(ground_mat, array([0.0, 0.0, 1.0]), 0.0))
scene.lights.append(Light(array([-2.0, -2.0, 3.0]), 5 * array([1.0, 0.2, 0.2])))
scene.lights.append(Light(array([ 2.0, -2.0, 3.0]), 5 * array([0.2, 1.0, 0.2])))
scene.lights.append(Light(array([ 0.0,  0.0, 5.0]), 5 * array([0.2, 0.2, 1.0])))
texture = pygame.image.load("texture.jpg")
texture_size = texture.get_size()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
start = time.time()
scene.render(screen)
stop = time.time()
print "Rendered in: %.3f" % (stop - start)
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == 27):
			pygame.quit()
			exit()
		if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
			pygame.image.save(screen, "output2.png")
			print "Saved."
	pygame.display.update()
	time.sleep(0.01)

