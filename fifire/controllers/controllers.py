# -*- coding: utf-8 -*-
# from odoo import http


# class Fifire(http.Controller):
#     @http.route('/fifire/fifire', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fifire/fifire/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fifire.listing', {
#             'root': '/fifire/fifire',
#             'objects': http.request.env['fifire.fifire'].search([]),
#         })

#     @http.route('/fifire/fifire/objects/<model("fifire.fifire"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fifire.object', {
#             'object': obj
#         })
