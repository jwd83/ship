import pyglet


class Point:
    def __init__(self, x, y):
        self.x = None
        self.y = None
        self.set(x, y)

    def set(self, x=None, y=None):
        self.x = self.x if x is None else x
        self.y = self.y if y is None else y

    def get(self):
        return self.x, self.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Poly:
    def __init__(self, anchor_x, anchor_y):
        self._anchor = Point(anchor_x, anchor_y)
        self._points = []
        self._final_points = []
        self.top = None
        self.bottom = None
        self.left = None
        self.right = None

    def set_limit(self):
        self.top = None
        self.bottom = None
        self.left = None
        self.right = None

        if len(self._final_points) > 0:
            self.top = self._final_points[0].y
            self.bottom = self._final_points[0].y
            self.left = self._final_points[0].x
            self.right = self._final_points[0].x

        for pt in self._final_points:
            if pt.y > self.top: self.top = pt.y
            if pt.y < self.bottom: self.bottom = pt.y
            if pt.x > self.right: self.right = pt.x
            if pt.x < self.left: self.left = pt.x

    def add_point(self, x, y):
        self._points.append(Point(x, y))
        self._final_points.append(Point(self._anchor.x + x, self._anchor.y + y))

    def move(self, anchor_x, anchor_y):
        # create a new anchor point
        self._anchor = Point(anchor_x, anchor_y)

        # reset our final points
        self._final_points = []

        # recalculate final points
        for pt in self._points:
            self._final_points.append(Point(self._anchor.x + pt.x, self._anchor.y + pt.y))

    def add_to_batch(self, batch):
        pt_count = len(self._final_points)
        # print(pt_count)
        for i in range(pt_count):
            # print(i)
            x1 = self._final_points[i].x
            y1 = self._final_points[i].y

            if i == pt_count - 1:
                x2 = self._final_points[0].x
                y2 = self._final_points[0].y
            else:
                x2 = self._final_points[i + 1].x
                y2 = self._final_points[i + 1].y

            batch.add(2, pyglet.gl.GL_LINES, None,
                      ('v2f', (x1, y1, x2, y2)),
                      ('c3B', (255, 0, 0, 255, 0, 0))  # c3B is a gradient (0,0,0, 255,255,255) combo
                      # this gradient will be per line, not end to end.
                      )

    def point_inside(self, p: Point):
        #  c routine from stack overflow
        #
        # https://stackoverflow.com/questions/11716268/point-in-polygon-algorithm
        #
        # int pnpoly(int nvert, float *vertx, float *verty, float testx, float testy)
        # {
        #   int i, j, c = 0;
        #   for (i = 0, j = nvert-1; i < nvert; j = i++) {
        #     if ( ((verty[i]>testy) != (verty[j]>testy)) &&
        #
        #        c = !c;
        #   }
        #   return c;
        # }

        inside = False
        number_of_vertices = len(self._final_points)

        j = number_of_vertices - 1
        for i in range(number_of_vertices):
            if (self._final_points[i].y > p.y) != (self._final_points[j].y > p.y):
                if p.x < \
                        (self._final_points[j].x - self._final_points[i].x) * (p.y - self._final_points[i].y) \
                        / (self._final_points[j].y - self._final_points[i].y) \
                        + self._final_points[i].x:
                    inside = not inside
            j = i
        return inside

    def _ccw(self, A: Point, B: Point, C: Point):
        return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)

    # Return true if line segments AB and CD intersect
    def _segment_intersect(self, A: Point, B: Point, C: Point, D: Point):
        return self._ccw(A, C, D) != self._ccw(B, C, D) and self._ccw(A, B, C) != self._ccw(A, B, D)

    def overlaps(self, poly):

        # check for line intersections or if a polygon is inside another

        # check each line segment for an intersection
        pt_count = len(self._final_points)
        pt_count_ol = len(poly._final_points)
        # print(pt_count)
        for i in range(pt_count):
            A = self._final_points[i]
            if i == pt_count - 1:
                B = self._final_points[0]
            else:
                B = self._final_points[i + 1]

            for j in range(pt_count_ol):
                C = poly._final_points[j]
                if j == pt_count_ol - 1:
                    D = poly._final_points[0]
                else:
                    D = poly._final_points[j + 1]

                if self._segment_intersect(A, B, C, D):
                    return True

        # if no lines intersect we need to check only if 1 point in either polygon is fully inside the other

        # check if self is inside provided poly
        if poly.point_inside(self._final_points[0]) or self.point_inside(poly._final_points[0]):
            return True

        # nothing was found, return false
        return False

    def __repr__(self):
        text = f"Polygon anchored at {self._anchor}\nPoints about anchor...\n"
        i = 1
        for pt in self._points:
            text += f"    Point #{i} at {pt}\n"
            i += 1

        return text


if __name__ == '__main__':
    square = Poly(10, 10)
    square.add_point(-5, -5)
    square.add_point(-5, 5)
    square.add_point(5, 5)
    square.add_point(5, -5)
    print(square)
    print(square.point_inside(Point(10, 10)))
    print(square.point_inside(Point(12, 12)))
    print(square.point_inside(Point(20, 20)))

    print("Creating second square")
    sqr2 = Poly(20, 20)
    sqr2.add_point(-2, -2)
    sqr2.add_point(-2, 2)
    sqr2.add_point(2, 2)
    sqr2.add_point(2, -2)
    print(sqr2)
    print(square.overlaps(sqr2))

    # move sqr2 fully inside square
    sqr2.move(10, 10)
    print(square.overlaps(sqr2))

    # move sqr2 on the top left edge of square so neither first point is inside one another
    sqr2.move(5, 15)
    print(square.overlaps(sqr2))

    # move sqr2 just outside the top left edge of square so neither overlap
    sqr2.move(2.9, 15)
    print(square.overlaps(sqr2))
