import numpy as np

import ptcv as pt_cv

from uuid import uuid4

ptcv = pt_cv.Ptcv()

ptframe_buffer_size = 1
ptframe_sync_tolerance = 10 # milliseconds

# I need a confidence increase / descrease function that looks like this
#           ..
#          .    .
# ___________________threshold (above the line is a known player)
#        .        .
#     .            .
# .                .
# ^ slow rap up in rate of change, and slow ram down

# Tuneables
MAX_DIST = 200
INITIAL_CONFIDENCE = 1 # initial confidence when seen for the first time
CONFIDENCE_INCREASE = 1 # confidence increase when seen
CONFIDENCE_REDUCTION = 1 # confidence reduction when not seen
ENOUGH_CONFIDENCE = -100 # enough confidence to be considered a player
MAX_CONFIDENCE = 100 # confidence of a player cannot grow beyond this value
MIN_CONFIDENCE = -100 # removed from player list if confidence gets this low

def set_tracking_options(max_dist=None,
                         initial_confidence=None,
                         confidence_increase=None,
                         confidence_reduction=None,
                         confidence_threshold=None,
                         max_confidence=None,
                         min_confidence=None):
    global MAX_DIST
    global INITIAL_CONFIDENCE
    global CONFIDENCE_INCREASE
    global CONFIDENCE_REDUCTION
    global ENOUGH_CONFIDENCE
    global MAX_CONFIDENCE
    global MIN_CONFIDENCE

    MAX_DIST = max_dist or MAX_DIST
    INITIAL_CONFIDENCE = initial_confidence or INITIAL_CONFIDENCE
    CONFIDENCE_INCREASE = confidence_increase or CONFIDENCE_INCREASE
    CONFIDENCE_REDUCTION = confidence_reduction or CONFIDENCE_REDUCTION
    ENOUGH_CONFIDENCE = confidence_threshold or ENOUGH_CONFIDENCE
    MAX_CONFIDENCE = max_confidence or MAX_CONFIDENCE
    MIN_CONFIDENCE = min_confidence or MIN_CONFIDENCE
    # print ("SETTINGS:",
    #     "\nmax_dist %s:" % MAX_DIST,
    #     "\ninitial_confidence %s:" % INITIAL_CONFIDENCE,
    #     "\nconfidence_increase %s:" % CONFIDENCE_INCREASE,
    #     "\nenough_confidence %s:" % ENOUGH_CONFIDENCE,
    #     "\nconfidence_reduction %s:" % CONFIDENCE_REDUCTION,
    #     "\nmax_confidence %s:" % MAX_CONFIDENCE,
    #     "\nmin_confidence %s:" % MIN_CONFIDENCE,
    # )

def framedict_to_ptframe(ptframe_dict):
    ptframe = PtFrame(ptframe_dict)
    return ptframe

def get_players(ptframes):
    players = []
    for ptframe in ptframes:
        players.extend(ptframe.players)
    return players

def draw_player_graphics(np_scene, players):
    for player in players:
        ptcv.put_circle(np_scene, (player['x'],player['y']))
        ptcv.put_text(np_scene, player['name'], (player['x'], player['y']))

def ptframes_to_grid(ptframes):
    assert ptframes != None, "no ptframes given: %s" % ptframes
    zone_ids = [ptframe.zone_id for ptframe in ptframes]
    zone_ids_are_unique = len(zone_ids) == len(set(zone_ids))
    assert zone_ids_are_unique, "zone ids are not unique: %s" % zone_ids

    x_coords = [ptframe.zone_x for ptframe in ptframes]
    y_coords = [ptframe.zone_y for ptframe in ptframes]
    x_coords.sort()
    y_coords.sort()
    max_x = max(x_coords)
    max_y = max(y_coords)

    # Initilize grid
    grid = np.zeros((max_x+1, max_y+1), dtype=object)

    for ptframe in ptframes:
        x = ptframe.zone_x
        y = ptframe.zone_y
        grid[x][y] = ptframe

    return grid

def stitch(ptframes):
    grid = ptframes_to_grid(ptframes)

    if grid.shape == (1,1):
        return grid[0][0].frame

    np_row = None
    np_scene = None
    for y in range(grid.shape[1]):
        for x in range(grid.shape[0]):
            # Build row
            frame = grid[x][y].frame
            if np_row == None:
                np_row = frame
            else:
                np_row = np.concatenate((np_row, frame), axis=1)
        # Add row to total scene
        if np_scene == None:
            np_scene = np_row
        else:
            np_scene = np.concatenate((np_scene, np_row), axis=2)
    return np_scene

def enforce_sync_tolerance(ptframes):
    # TODO LATER
    return ptframes

def calc_dist(loc_a, loc_b):
    # TODO: use tangent line instead of individual dimensions
    dist_x = abs(loc_a[0] - loc_b[0])
    dist_y = abs(loc_a[1] - loc_b[1])
    total_dist = sum([dist_x, dist_y])
    return total_dist

players = {}

def print_players():
    if not players:
        return
    # Table body
    for player_id, player in players.iteritems():
            print " %s | %s | %s | %s " % (len(players), player['id'], player['loc'], player['confidence'])

def identify_nearest_players(seen_locs):
    # For each loc found in the scene, add to the confidence of an existing loc if near enough
    # or add it to the saved list if not seen recently
    all_player_ids = [player_id for player_id, player in players.iteritems()]
    unseen_player_ids = all_player_ids

    # print_players()

    for loc in seen_locs:
        # find saved locations (players) that are close to this location (loc) and store it in matches
        matches = []
        for player_id, player in players.iteritems():
            dist = calc_dist(player['loc'], loc)
            if dist <= MAX_DIST:
                match = player.copy()
                match['dist'] = dist
                matches.append(match)

        if len(matches) > 1:
            # print "WARNING: More than 1 match!"
            # try to find the closest match
            closest = matches[0]
            for match in matches:
                if match['dist'] < closest['dist']:
                    closest = match
            matches = [closest]

        if len(matches) == 1:
            # update the player's location the match and increase the confidence in that player
            matched_id = matches[0]['id']
            players[matched_id]['loc'] = loc
            if matched_id in unseen_player_ids:
                unseen_player_ids.remove(matched_id)
            if players[matched_id]['confidence'] < MAX_CONFIDENCE:
                if not players[matched_id]['confidence']:
                    players[matched_id]['confidence'] = INITIAL_CONFIDENCE
                players[matched_id]['confidence'] += CONFIDENCE_INCREASE

        else:
            # this location is not near an existing player so it is new
            uuid = "%s" % uuid4()
            new_loc_to_save = {
                'loc': loc,
                'confidence': INITIAL_CONFIDENCE,
                'id': uuid
            }
            players[uuid] = new_loc_to_save

    # Reduce confidence and/or remove players
    for unseen_player_id in unseen_player_ids:
        players[unseen_player_id]['confidence'] -= CONFIDENCE_REDUCTION
        if players[unseen_player_id]['confidence'] < MIN_CONFIDENCE:
            players.pop(unseen_player_id)

    high_confidence_players = [player for player_id, player in players.iteritems() if player['confidence'] >= ENOUGH_CONFIDENCE]
    return high_confidence_players



class GameMap(object):
    def __init__(self):
        self.zones = []

    def get_all_ptframes(self):
        ptframes = []
        [ptframes.extend(zone.ptframes) for zone in self.zones]
        if not ptframes:
            # TODO: this should be a warning log statement
            raise Exception("No ptframes found: %s" % ptframes)

        return ptframes

    def add_zone(self, zone_id):
        self.zones.append(Zone(zone_id))

    def get_zone(self, zone_id):
        zone = [zone for zone in self.zones if zone.id == zone_id]
        if not zone:
            raise Exception("Zone with id '%s' not found!" % zone_id)
        return zone[0]

    def set_ptframe(self, ptframe):
        zone_ids = [zone.id for zone in self.zones]
        if ptframe.zone_id not in zone_ids:
            self.add_zone(ptframe.zone_id)
        zone = self.get_zone(ptframe.zone_id)
        zone.set_ptframe(ptframe)

    def get_ptframes(self):
        return [zone.ptframe for zone in self.zones]

    # def get_median_time(self):
    #     ptframes = self.get_all_ptframes()
    #     ptframes.sort(key=lambda x: x.time)
    #     median_ptframe = ptframes[len(ptframes)/2]
    #     return median_ptframe.time

    # def get_ptframes_nearest_time(self, req_time):
    #     ptframes = []
    #     for zone in self.zones:
    #         ptframes.append(zone.get_ptframe_nearest_time(req_time))
    #     if not ptframes:
    #         # TODO: this should be a warning log statement
    #         raise Exception("No ptframes found around time %s" % req_time)
    #     return ptframes

    def get_np_scene(self):
        # Get latest frames from buffer
        ptframes = self.get_ptframes()
        if not ptframes: return
        # Get frames from buffer in sync
        # median_time = self.get_median_time()
        # ptframes = self.get_ptframes_nearest_time(median_time)
        # ptframes = enforce_sync_tolerance(ptframes)

        ##
        # from copy import copy
        # extra_ptframe = copy(ptframes[0])
        # extra_ptframe.zone_id = 1
        # extra_ptframe.zone_x = 1
        # extra_ptframe.zone_y = 0
        # extra_ptframe.players = [{
        #     'name':'Mac',
        #     'x': 600,
        #     'y': 400
        # }]
        # ptframes.append(extra_ptframe)
        # ##

        players = get_players(ptframes)
        np_scene = stitch(ptframes)
        draw_player_graphics(np_scene, players)
        return np_scene

class Zone(object):
    def __init__(self, id):
        self.id = id
        self.ptframe = None

    def set_ptframe(self, ptframe):
        # assert isinstance(ptframe, PtFrame), "%r is not a ptframe" % ptframe
        self.ptframe = ptframe

    def get_ptframe(self, ptframe):
        return self.ptframe

    # def get_ptframe_nearest_time(self, req_time):
    #     closest_ptframe = None
    #     closest_time_diff = 999999
    #     for ptframe in self.ptframes:
    #         time_diff = abs(req_time - ptframe.time)
    #         if time_diff < closest_time_diff:
    #             closest_ptframe = ptframe
    #             closest_time_diff = time_diff
    #     if not closest_ptframe:
    #         # TODO: this should be a warning log statement
    #         raise Exception("No ptframe found around time %s" % req_time)
    #     return ptframe


class PtFrame(object):
    def __init__(self, frame_dict):
        # np_frame = ptcv.str_to_npframe(frame_dict['frame'])
        self.frame = frame_dict['frame']
        self.time = frame_dict['time']
        self.frame_id = frame_dict['frame_id']
        self.zone_id = frame_dict['zone_id']
        self.zone_x = frame_dict['zone_x']
        self.zone_y = frame_dict['zone_y']
        self.players = frame_dict['players']
