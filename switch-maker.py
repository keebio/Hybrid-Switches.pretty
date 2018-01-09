#!/usr/bin/env python

from KicadModTree import *

class KeyboardSwitchMaker(object):
    """docstring for KeyboardSwitchMaker"""
    def __init__(self):
        self.switch_pads = {
            'mx': [(-3.81, -2.54), (2.54, -5.08)],
            'alps': [(-2.5, -4), (2.5, -4.5)],
            'choc': []
        }
        self.support_holes = {
            'mx': {'locations': [(-5.08, 0), (5.08, 0)], 'size': 1.8},
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

    def make_switch(self, name, size):
        fp = Footprint(name)
        fp.setDescription('MX/Alps footprint')
        sw_types = ['mx', 'alps']

        # Annotations
        fp.append(Text(type='reference', text='REF**', at=[0, 7.9375], layer='Dwgs.User'))
        fp.append(Text(type='value', text='{}u'.format(size), at=[0, -7.9375], layer='Dwgs.User'))

        self.add_borders(fp, size)
        self.add_cutouts(fp, sw_types)
        self.add_switch_pads(fp, sw_types)
        self.add_led_pads(fp, sw_types)
        self.add_support_holes(fp, sw_types)
        self.add_stabilizers(fp)

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
        for sw_type in sw_types:
            pads = self.switch_pads[sw_type]
            pad_size = 2.25
            drill_size = 1.47
            fp.append(Pad(number=1, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=pads[0], size=[pad_size, pad_size], drill=drill_size, layers=Pad.LAYERS_THT))
            fp.append(Pad(number=2, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=pads[1], size=[pad_size, pad_size], drill=drill_size, layers=Pad.LAYERS_THT))

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
            if self.support_holes.get(sw_type) is None:
                continue
            drill_size = self.support_holes[sw_type]['size']
            for hole_location in self.support_holes[sw_type]['locations']:
                fp.append(Pad(type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, at=hole_location, size=[drill_size, drill_size], drill=drill_size, layers=Pad.LAYERS_NPTH))

    def add_stabilizers(self, fp):
        return


    def oval_dimensions(pad1, pad2):
        return {}

    def make_switches(self):
        sizes = [1, 1.25]
        for size in sizes:
            name = 'MX-Alps-{}u'.format(size)
            self.make_switch(name, size)

m = KeyboardSwitchMaker()
m.make_switches()
