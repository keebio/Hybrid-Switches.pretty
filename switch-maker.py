#!/usr/bin/env python

from KicadModTree import *
import math

class KeyboardSwitchMaker(object):
    """docstring for KeyboardSwitchMaker"""
    def __init__(self):
        self.switch_pads = {
            'mx': [(-3.81, -2.54), (2.54, -5.08)],
            'alps': [(-2.5, -4), (2.5, -4.5)],
            'choc': []
        }
        self.support_holes = {
            'mx': {'locations': [(-5.08, 0), (5.08, 0)], 'size': 1.75},
            'choc': []
        }
        self.stabilizer_big_holes = {
            'mx': {'locations': [(-11.938, 8.255), (11.938, 8.255)], 'size': 3.9878},
            'choc': []
        }
        self.stabilizer_small_holes = {
            'mx': {'locations': [(-11.938, -6.985), (11.938, -6.985)], 'size': 3.048},
            'choc': []
        }
        self.led_pads = {
            'mx': [(-1.27, 5.08), (1.27, 5.08)],
            'choc': []
        }
        self.cutout_size = {
            'mx': (14.0, 14.0),
            'alps': (15.5, 12.8),
            'choc': (14.0, 14.0)
        }
        self.switch_spacing = 19.05
        self.type_names = {'mx': 'MX', 'alps': 'Alps', 'choc': 'Choc'}

    def make_switch(self, name, size, sw_types):
        fp = Footprint(name)
        fp.setDescription('MX/Alps footprint')

        # Annotations
        fp.append(Text(type='reference', text='REF**', at=[0, 7.9375], layer='Dwgs.User'))
        fp.append(Text(type='value', text='{}u'.format(size), at=[0, -7.9375], layer='Dwgs.User'))

        self.add_borders(fp, size)
        self.add_cutouts(fp, sw_types)
        self.add_switch_pads(fp, sw_types)
        self.add_led_pads(fp, sw_types)
        self.add_support_holes(fp, sw_types)
        if size >= 2:
            self.add_stabilizers(fp, sw_types)

        # Write
        filename = '{}.kicad_mod'.format(name)
        file_handler = KicadFileHandler(fp)
        file_handler.writeFile(filename)
        print 'Wrote {}'.format(filename)

    def add_borders(self, fp, size):
        width = size * self.switch_spacing
        height = 1.0 * self.switch_spacing
        self.add_box(fp, width, height, 'Dwgs.User')

    def add_switch_pads(self, fp, sw_types):
        # Collect pads for combining
        pad1_locations = [self.switch_pads[sw_type][0] for sw_type in sw_types]
        pad2_locations = [self.switch_pads[sw_type][1] for sw_type in sw_types]

        # Only one switch type
        if len(sw_types) == 1:
            for pad in pad1_locations:
                self.add_normal_pad(fp, 1, pad)
            for pad in pad2_locations:
                self.add_normal_pad(fp, 2, pad)
            return

        # Add hybrid with first pad drilled
        self.add_hybrid_pad(fp, 1, pad1_locations)
        self.add_hybrid_pad(fp, 2, pad2_locations)

        # Add remaining pads
        for pad in pad1_locations[1:]:
            self.add_normal_pad(fp, 1, pad)
        for pad in pad2_locations[1:]:
            self.add_normal_pad(fp, 2, pad)

    def add_hybrid_pad(self, fp, pad_number, pads):
        height = 2.25
        drill_size = 1.47
        width = self.pad_distance(pads) + height
        location = self.oval_location(pads)
        angle = self.oval_angle(pads)
        offset = -self.pad_distance(pads)/2
        print offset
        fp.append(Pad(
            number=pad_number,
            type=Pad.TYPE_THT,
            shape=Pad.SHAPE_OVAL,
            at=pads[0],
            rotation=angle,
            size=[height, width],
            offset=[0, offset],
            drill=drill_size,
            layers=Pad.LAYERS_THT))

    def pad_distance(self, locations):
        pad1, pad2 = locations[0:2]
        return math.sqrt((pad1[0] - pad2[0]) ** 2 + (pad1[1] - pad2[1]) ** 2)

    def oval_location(self, locations):
        pad1, pad2 = locations[0:2]
        return ((pad1[0] + pad2[0])/2, (pad1[1] + pad2[1])/2)

    def oval_angle(self, locations):
        pad1, pad2 = locations[0:2]
        return math.degrees(math.atan2(pad1[0] - pad2[0], pad1[1] - pad2[1]))

    def add_normal_pad(self, fp, pad_number, pad):
        pad_size = 2.25
        drill_size = 1.47
        fp.append(Pad(number=pad_number, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=pad, size=[pad_size, pad_size], drill=drill_size, layers=Pad.LAYERS_THT))

    def add_led_pads(self, fp, sw_types):
        pad_size = 1.905
        drill_size = 0.9906
        pads = self.led_pads[sw_types[0]]
        fp.append(Pad(number=3, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=pads[0], size=[pad_size, pad_size], drill=drill_size, layers=Pad.LAYERS_THT))
        fp.append(Pad(number=4, type=Pad.TYPE_THT, shape=Pad.SHAPE_RECT, at=pads[1], size=[pad_size, pad_size], drill=drill_size, layers=Pad.LAYERS_THT))
        for layer in ('F.SilkS', 'B.SilkS'):
            fp.append(Text(type='user', text='+', at=[pads[0][0], 3.5], layer=layer))
            fp.append(Text(type='user', text='-', at=[pads[1][0], 3.5], layer=layer))

    def add_cutouts(self, fp, sw_types):
        for sw_type in sw_types:
            width, height = self.cutout_size[sw_type]
            self.add_box(fp, width, height, 'Cmts.User')

    def add_box(self, fp, width, height, layer):
        top_left = (-width/2, -height/2)
        top_right = (width/2, -height/2)
        bottom_left = (-width/2, height/2)
        bottom_right = (width/2, height/2)
        fp.append(RectLine(start=top_left, end=top_right, layer=layer))
        fp.append(RectLine(start=top_left, end=bottom_left, layer=layer))
        fp.append(RectLine(start=top_right, end=bottom_right, layer=layer))
        fp.append(RectLine(start=bottom_left, end=bottom_right, layer=layer))

    def add_support_holes(self, fp, sw_types):
        drill_size = 3.9878
        fp.append(Pad(type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, at=[0, 0], size=[drill_size, drill_size], drill=drill_size, layers=Pad.LAYERS_NPTH))

        for sw_type in sw_types:
            if self.stabilizer_big_holes.get(sw_type) is None:
                continue
            drill_size = self.stabilizer_big_holes[sw_type]['size']
            for hole_location in self.stabilizer_big_holes[sw_type]['locations']:
                fp.append(Pad(type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, at=hole_location, size=[drill_size, drill_size], drill=drill_size, layers=Pad.LAYERS_NPTH))

    def add_stabilizers(self, fp, sw_types):
        for sw_type in sw_types:
            for holes in [self.stabilizer_big_holes, self.stabilizer_small_holes]:
                if holes.get(sw_type) is None:
                    continue
                drill_size = holes[sw_type]['size']
                for hole_location in holes[sw_type]['locations']:
                    fp.append(Pad(type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, at=hole_location, size=[drill_size, drill_size], drill=drill_size, layers=Pad.LAYERS_NPTH))
        return

    def make_switches(self):
        sizes = [1, 1.25, 1.5, 1.75, 2.25]
        hybrid_types = [
            ['mx'],
            #['mx', 'alps']
        ]
        for size in sizes:
            for hybrid_type in hybrid_types:
                hybrid_name = '-'.join(self.type_names[sw_type] for sw_type in hybrid_type)
                name = '{}-{}u'.format(hybrid_name, size)
                self.make_switch(name, size, hybrid_type)

m = KeyboardSwitchMaker()
m.make_switches()
