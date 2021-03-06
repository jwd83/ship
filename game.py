import pyglet
import random
from pyglet.window import key
from projectile import Projectile
from polys import *

FRAME_RATE = 60
WIDTH = 1280
HEIGHT = 720
HEADER = 40
SPEED_SHIP = 170
SPEED_PLASMA = 400
SPEED_GALAXY = -30
SPEED_STAR = -70
PLASMA_CD = 0.3
COUNT_STARS = 100
COUNT_GALAXIES = 10
SCALE_STARS = 0.55

main_batch = pyglet.graphics.Batch()

bg_layer_1 = pyglet.graphics.OrderedGroup(0)
bg_layer_2 = pyglet.graphics.OrderedGroup(1)
fg_layer_1 = pyglet.graphics.OrderedGroup(2)


def create_rectangle_hitbox(s: pyglet.sprite.Sprite):
    h = Poly(0, 0)
    h.add_point(0, 0)
    h.add_point(0, s.height)
    h.add_point(s.width, s.height)
    h.add_point(s.width, 0)
    h.move(s.x, s.y)
    return h


class GameWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        # create our pyglet window
        super().__init__(*args, **kwargs)

        # setup key handling
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        # setup debug text
        self.debug_str = ""
        self.label_debug = pyglet.text.Label(
            self.debug_str,
            font_name='Arial',
            font_size=18,
            x=0,
            y=self.height,
            anchor_x='left',
            anchor_y='top',
            batch=main_batch
        )
        self.debug_enable = True

        # load sprites
        # player
        self.image_player = pyglet.image.load('van.png')
        self.image_plasma = pyglet.image.load('plasma.png')

        # stars
        self.image_star_white = pyglet.image.load('star-white.png')
        self.image_star_red = pyglet.image.load('star-red.png')
        self.image_star_blue = pyglet.image.load('star-blue.png')

        # galaxy/nebula
        self.image_galaxy = pyglet.image.load('galaxy.png')
        self.image_galaxy_white = pyglet.image.load('galaxy-white.png')
        self.image_galaxy_blue = pyglet.image.load('galaxy-blue.png')
        self.image_nebula_red = pyglet.image.load('nebula-red.png')
        self.image_nebula_green = pyglet.image.load('nebula-green.png')
        self.image_nebula_blue = pyglet.image.load('nebula-blue.png')

        self.image_go_subwayo = pyglet.image.load('go-subwayo.png')

        self.sfx_plasma = pyglet.media.load('plasma.wav', streaming=False)
        self.sin = pyglet.media.procedural.Sine(0.05, 2200)
        self.sin.play()

        self.player = pyglet.sprite.Sprite(self.image_player, x=100, y=HEIGHT // 2, batch=main_batch, group=fg_layer_1)
        # self.player.scale = 1.5
        self.player.vx = 0
        self.player.vy = 0
        self.player.hitbox = create_rectangle_hitbox(self.player)
        self.player.cooldown_plasma = PLASMA_CD
        self.player.projectiles = []
        self.galaxies = []
        self.stars = []
        self.enemies = []

        gn_images = [
            self.image_nebula_red,
            self.image_nebula_blue,
            self.image_nebula_green,
            self.image_galaxy_white,
            self.image_galaxy_blue
        ]

        for i in range(10):
            g = pyglet.sprite.Sprite(self.image_go_subwayo, x=(2+i) * WIDTH, y=random.randint(0, 600), batch=main_batch,
                                     group=fg_layer_1)
            g.vx = -100
            self.enemies.append(g)

        for i in range(COUNT_GALAXIES):
            xmin = int(i / COUNT_GALAXIES * WIDTH)
            xmax = int((i+1) / COUNT_GALAXIES * WIDTH)
            #
            # c = random.uniform(0.0, 1.0)
            # if c > 0.5:
            #     galaxy_img = self.image_galaxy_white
            # else:
            #     galaxy_img = self.image_nebula_red

            galaxy_img = random.choice(gn_images)
            g = pyglet.sprite.Sprite(galaxy_img, x=random.randint(xmin, xmax), y=random.randint(0, 600),
                                     batch=main_batch, group=bg_layer_1)

            nearness = random.uniform(0.7, 1.0)
            g.vx = SPEED_GALAXY * nearness
            # g.scale *= nearness

            g.rotation = random.randint(0, 359)
            self.galaxies.append(g)

        for i in range(COUNT_STARS):

            c = random.uniform(0.0, 1.0)
            if c > 0.9:
                star_img = self.image_star_blue
            elif c > 0.8:
                star_img = self.image_star_red
            else:
                star_img = self.image_star_white

            g = pyglet.sprite.Sprite(star_img, x=random.randint(0, 1300), y=random.randint(0, 660),
                                     batch=main_batch, group=bg_layer_2)
            nearness = random.uniform(0.4, 1.0)
            g.vx = SPEED_STAR * nearness
            g.scale = SCALE_STARS * nearness * nearness
            self.stars.append(g)


    def on_draw(self):
        frame_batch = pyglet.graphics.Batch()

        self.clear()

        # draw the debugging string if requested
        if self.debug_enable:
            self.debug_str = f"Projectiles: {len(self.player.projectiles)}"
            self.label_debug.text = self.debug_str
            # self.label_debug.batch = batch

        # prepare batch
        # batch.add(self.player)
        # batch.add(self.label_debug)
        self.player.hitbox.add_to_batch(frame_batch)
        for p in self.player.projectiles:
            p.hitbox.add_to_batch(frame_batch)

        # render batch
        main_batch.draw()
        # frame_batch.draw()

        # clean up the debugging string
        self.debug_str = ""

    def update(self, dt):
        # update player
        self.update_player(dt)
        self.update_projectiles(dt)
        self.update_background(dt)
        self.update_enemies(dt)

    def update_enemies(self, dt):
        for g in self.enemies:
            g.x += g.vx * dt

    def update_background(self, dt):
        for g in self.galaxies:
            g.x += g.vx * dt

            if g.x < -g.width:
                g.x = WIDTH + g.width * 2
                g.rotation = random.randint(0,359)
                g.y = random.randint(0, 600)

        for g in self.stars:
            g.x += g.vx * dt

            if g.x < -g.width:
                g.x = 1300
                g.y = random.randint(0, 660)

    def update_projectiles(self, dt):
        # update player projectiles and remove projectiles out of bounds
        inbound_projectiles = []
        for p in self.player.projectiles:
            p.update(dt)
            if p.x < WIDTH:
                inbound_projectiles.append(p)
            else:
                pass
                # todo - check if this is necessary. it does not appear to be
                # p.batch = None

        self.player.projectiles = inbound_projectiles

    def update_player(self, dt):
        # update motion
        if self.keys[key.LEFT] and self.keys[key.RIGHT]:
            self.player.vx = 0
        else:
            if self.keys[key.LEFT]:
                self.player.vx = -1
            elif self.keys[key.RIGHT]:
                self.player.vx = 1
            else:
                self.player.vx = 0

        if self.keys[key.UP] and self.keys[key.DOWN]:
            self.player.vy = 0
        else:
            if self.keys[key.UP]:
                self.player.vy = 1
            elif self.keys[key.DOWN]:
                self.player.vy = -1
            else:
                self.player.vy = 0

        self.player.x += self.player.vx * dt * SPEED_SHIP
        self.player.y += self.player.vy * dt * SPEED_SHIP
        if self.player.x < 0: self.player.x = 0
        if self.player.x + self.player.width > WIDTH:
            self.player.x = WIDTH - self.player.width
        if self.player.y < 0: self.player.y = 0
        if self.player.y + self.player.height > HEIGHT - HEADER:
            self.player.y = HEIGHT - HEADER - self.player.height

        self.player.hitbox.move(self.player.x, self.player.y)

        # update shooting
        self.player.cooldown_plasma -= dt
        if self.player.cooldown_plasma <= 0 and self.keys[key.SPACE]:
            self.player.cooldown_plasma = PLASMA_CD
            new_projectile = Projectile(
                self.image_plasma,
                x=self.player.x + self.player.width,
                y=self.player.y + self.player.height // 2,
                batch=main_batch,
                group=fg_layer_1
            )
            new_projectile.hitbox = create_rectangle_hitbox(new_projectile)
            new_projectile.velocity_x = SPEED_PLASMA
            self.player.projectiles.append(new_projectile)
            self.sfx_plasma.play()



if __name__ == "__main__":
    window = GameWindow(1280, 720, "Van Alien")
    pyglet.clock.schedule_interval(window.update, 1.0 / FRAME_RATE)
    pyglet.app.run()
