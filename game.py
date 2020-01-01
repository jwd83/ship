import pyglet
from pyglet.window import key

from polys import *

FRAME_RATE = 60
WIDTH = 1280
HEIGHT = 720
SHIP_SPEED = 500

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
        player_image = pyglet.image.load('astrominer.png')
        self.player = pyglet.sprite.Sprite(player_image, x=100, y=HEIGHT // 2, batch=main_batch)
        self.player.vx = 0
        self.player.vy = 0
        self.player.rect = Poly(0, 0)
        self.player.rect.add_point(0, 0)
        self.player.rect.add_point(0, 0)
        self.player.rect.add_point(0, 0)
        self.player.rect.add_point(0, 0)
        self.player.rect.move(self.player.x, self.player.y)

    def on_draw(self):
        frame_batch = pyglet.graphics.Batch()

        self.player.rect.move(self.player.x, self.player.y)

        self.clear()

        # draw the debugging string if requested
        if self.debug_enable:
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
        # handle left/right movement
        self.update_player(dt)

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

        self.player.x += self.player.vx * dt * SHIP_SPEED
        self.player.y += self.player.vy * dt * SHIP_SPEED


if __name__ == "__main__":
    window = GameWindow(1280, 720, "GR")
    pyglet.clock.schedule_interval(window.update, 1.0 / FRAME_RATE)
    pyglet.app.run()
