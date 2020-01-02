import pyglet
from pyglet.window import key
from projectile import Projectile
from polys import *

FRAME_RATE = 60
WIDTH = 1280
HEIGHT = 720
SPEED_SHIP = 170
SPEED_PLASMA = 400
PLASMA_CD = 0.15

main_batch = pyglet.graphics.Batch()


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

        # setup player
        self.image_player = pyglet.image.load('van.png')
        self.image_plasma = pyglet.image.load('plasma.png')

        self.player = pyglet.sprite.Sprite(self.image_player, x=100, y=HEIGHT // 2, batch=main_batch)
        self.player.vx = 0
        self.player.vy = 0
        self.player.rect = Poly(0, 0)
        self.player.rect.add_point(0, 0)
        self.player.rect.add_point(0, self.player.height)
        self.player.rect.add_point(self.player.width, self.player.height)
        self.player.rect.add_point(self.player.width, 0)
        self.player.rect.move(self.player.x, self.player.y)
        self.player.cooldown_plasma = PLASMA_CD
        self.player.projectiles = []

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
        self.player.rect.add_to_batch(frame_batch)

        # render batch
        main_batch.draw()
        frame_batch.draw()

        # clean up the debugging string
        self.debug_str = ""

    def update(self, dt):
        # update player
        self.update_player(dt)

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
        self.player.rect.move(self.player.x, self.player.y)

        # update shooting
        self.player.cooldown_plasma -= dt
        if self.player.cooldown_plasma <= 0 and self.keys[key.SPACE]:
            self.player.cooldown_plasma = PLASMA_CD
            new_projectile = Projectile(
                self.image_plasma,
                x=self.player.x + self.player.width,
                y=self.player.y + self.player.height // 2,
                batch=main_batch
            )
            new_projectile.velocity_x = SPEED_PLASMA
            self.player.projectiles.append(new_projectile)


if __name__ == "__main__":
    window = GameWindow(1280, 720, "Van Alien")
    pyglet.clock.schedule_interval(window.update, 1.0 / FRAME_RATE)
    pyglet.app.run()
