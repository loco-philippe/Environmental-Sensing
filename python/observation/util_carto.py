# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 09:08:54 2023

@author: philippe@loco-labs.io
"""

import folium


class Cart:
    """folium map with markers"""

    def __init__(self, location=None, zoom_start=5):
        self.map = folium.Map(location=location, zoom_start=zoom_start)

    def add_markers(self, location, **kwargs):
        """add markers with popup in a layer group"""
        opt = {
            "popup": None,
            "max_width": 150,
            "icon": "bomb",
            "color": "blue",
            "group": None,
        } | kwargs
        grp = self.map
        color = opt["color"]
        if opt["group"]:
            grp = folium.map.FeatureGroup(opt["group"])
            grp.add_to(self.map)
        if opt["popup"]:
            for loc, pop in zip(location, opt["popup"]):
                icon = folium.Icon(color=color, icon=opt["icon"], prefix="fa")
                txt = folium.Popup(Cart.html(pop), max_width=opt["max_width"])
                folium.Marker(location=loc, popup=txt, icon=icon).add_to(grp)
        else:
            for loc in location:
                icon = folium.Icon(color=color, icon=opt["icon"], prefix="fa")
                folium.Marker(location=loc, icon=icon).add_to(grp)

    def show(self, mapname=None):
        """return the map and save it if mapname is present"""
        folium.LayerControl().add_to(self.map)
        if mapname:
            self.map.save(mapname)
        return self.map

    @staticmethod
    def html(dic):
        """return an html string from a dict"""
        pop = ""
        for key, val in dic.items():
            pop += "<div>" + "<b>" + str(key) + "</b>" + " : " + str(val) + "</div>"
        return pop
