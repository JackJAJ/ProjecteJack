# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class player(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    #_description = 'Player in the Game'

    #name = fields.Char(string='Player Name', required=True)
    coins = fields.Integer(string='Coins', default=0)
    upgrade_points = fields.Integer(string='Upgrade Points', default=0)
    heroes = fields.One2many('fifire.hero', 'player_id', string='Heroes')
    towers = fields.One2many('fifire.tower', 'player_id', string='Towers')
    armies = fields.One2many('fifire.army', 'player_id', string='Armies')

    @api.model
    def create(self, values):
        player_instance = super(player, self).create(values)
        player_instance._create_default_heroes()
        player_instance._create_default_towers()
        player_instance._create_default_army()

        return player_instance

    def add_upgrade_points(self, points):
        self.heroes.write({'upgrade_points': points})

    def get_defence_tower(self):
        return self.towers.filtered(lambda t: t.tower_type == 'defence')[:1]

    def get_strongest_heroes(self):
        return self.heroes.sorted(key=lambda hero: hero.strength, reverse=True)[:3]

    def _create_default_heroes(self):
        hero_data = [
            {'name': 'Lewis Hall', 'pace': 43, 'strength': 20, 'agility': 40, 'defence': 40, 'hero_type': 'cheetah'},
            {'name': 'Philip Billing', 'pace': 32, 'strength': 45, 'agility': 20, 'defence': 40, 'hero_type': 'bull'},
            {'name': 'Noni Madueke', 'pace': 72, 'strength': 25, 'agility': 75, 'defence': 40, 'hero_type': 'lynx'},
            {'name': 'Harvey Elliott', 'pace': 68, 'strength': 18, 'agility': 70, 'defence': 30, 'hero_type': 'lynx'},
            {'name': 'Lesley Uguchukwu', 'pace': 52, 'strength': 55, 'agility': 50, 'defence': 70, 'hero_type': 'armadillo'},
            {'name': 'Tino Livramento', 'pace': 62, 'strength': 45, 'agility': 50, 'defence': 60, 'hero_type': 'cheetah'},
            {'name': 'Anderson Talisca', 'pace': 62, 'strength': 48, 'agility': 60, 'defence': 40, 'hero_type': 'cheetah'},
            {'name': 'Craig Dawson', 'pace': 30, 'strength': 65, 'agility': 24, 'defence': 70, 'hero_type': 'armadillo'},
            {'name': 'Antonio Rudiger', 'pace': 72, 'strength': 85, 'agility': 70, 'defence': 83, 'hero_type': 'bull'},
            {'name': 'Bashir Humphreys', 'pace': 52, 'strength': 55, 'agility': 40, 'defence': 60, 'hero_type': 'armadillo'},
            {'name': 'Raheem Sterling', 'pace': 80, 'strength': 40, 'agility': 85, 'defence': 40, 'hero_type': 'lynx'}            
        ]

        heroes = self.env['fifire.hero'].create(hero_data)
        self.write({'heroes': [(6, 0, heroes.ids)]})

    def _create_default_towers(self):
        tower_data = [
            {'name': 'Wilder', 'tower_type': 'strength'},
            {'name': 'Cooper', 'tower_type': 'pace'},
            {'name': 'Edwards', 'tower_type': 'agility'},
            {'name': 'Iraola', 'tower_type': 'defence'},
        ]
        towers = [(0, 0, data) for data in tower_data]
        self.write({'towers': towers})

    def _create_default_army(self):
        tower = self.towers.filtered(lambda t: t.name == 'Wilder')[:1]

        if tower and not self.armies:
            army_data = {
                'name': "{}'s Army".format(self.name),
                'player_id': self.id,
                'tower_id': tower.id,
            }

            army = self.env['fifire.army'].create(army_data)

            hero_data = [
                {'name': hero.name, 'pace': hero.pace, 'strength': hero.strength, 'agility': hero.agility,
                'defence': hero.defence, 'hero_type': hero.hero_type}
                for hero in self.heroes[:11]
            ]
            heroes = self.env['fifire.hero'].create(hero_data)
            army.write({'heroes': [(6, 0, heroes.ids)]})

    @api.constrains('upgrade_points')
    def _check_upgrade_points_limit(self):
        for player in self:
            if player.upgrade_points > 100:
                raise exceptions.ValidationError("Upgrade points cannot exceed 100.")




class hero(models.Model):
    _name = 'fifire.hero'
    _description = 'Hero in the Game'

    name = fields.Char(string='Hero Name', required=True)
    pace = fields.Integer(string='Pace')
    strength = fields.Integer(string='Strength')
    agility = fields.Integer(string='Agility')
    defence = fields.Integer(string='Defence')
    health = fields.Integer(string='Health', default=100)
    hero_type = fields.Selection([
        ('cheetah', 'Cheetah'),
        ('bull', 'Bull'),
        ('lynx', 'Lynx'),
        ('armadillo', 'Armadillo')],
        string='Hero Type', compute='_compute_hero_type', store=True)
    
    player_id = fields.Many2one('res.partner', string='Player')

    level = fields.Integer(string='Level', default=1, readonly=True)
    upgrade_points = fields.Integer(string='Upgrade Points', default=0)

    upgraded_attribute_1 = fields.Float(string='Upgraded Attribute 1', compute='_compute_upgraded_attributes', store=True)
    upgraded_attribute_2 = fields.Float(string='Upgraded Attribute 2', compute='_compute_upgraded_attributes', store=True)

    @api.depends('pace', 'strength', 'agility', 'defence')
    def _compute_hero_type(self):
        for hero in self:
            highest_attribute = max(hero.pace, hero.strength, hero.agility, hero.defence)
            if highest_attribute == hero.pace:
                hero.hero_type = 'cheetah'
            elif highest_attribute == hero.strength:
                hero.hero_type = 'bull'
            elif highest_attribute == hero.agility:
                hero.hero_type = 'lynx'
            elif highest_attribute == hero.defence:
                hero.hero_type = 'armadillo'

    @api.depends('upgrade_points', 'pace', 'strength', 'agility', 'defence')
    def _compute_upgraded_attributes(self):
        for hero in self:
            total_upgrade_percentage = hero.upgrade_points / 10.0
            hero.upgraded_attribute_1 = hero.pace * (1 + total_upgrade_percentage * 0.005)
            hero.upgraded_attribute_2 = hero.strength * (1 + total_upgrade_percentage * 0.005)

    @api.constrains('level')
    def _check_level_limit(self):
        for hero in self:
            if hero.level > 10:
                raise exceptions.ValidationError("Hero's level cannot exceed 10.")
        
    def action_open_hero_details(self):
        return {
            'name': 'Hero Details',
            'type': 'ir.actions.act_window',
            'res_model': 'fifire.hero',
            'view_mode': 'form',
            'view_id': False, 
            'target': 'current',
            'res_id': self.id
        }


class tower(models.Model):
    _name = 'fifire.tower'
    _description = 'Tower in the Game'

    name = fields.Char(string='Tower Name', required=True)
    health = fields.Integer(string='Health', default=100)
    tower_type = fields.Selection([
        ('pace', 'Pace'),
        ('strength', 'Strength'),
        ('agility', 'Agility'),
        ('defence', 'Defence')],
        string='Tower Type', required=True)
    boost_attribute = fields.Char(string='Boost Attribute', compute='_compute_boost_attribute', store=True)
    player_id = fields.Many2one('res.partner', string='Player', required=True)

    @api.depends('tower_type')
    def _compute_boost_attribute(self):
        for tower in self:
            tower.boost_attribute = tower.tower_type




class army(models.Model):
    _name = 'fifire.army'
    _description = 'Army in the Game'

    name = fields.Char(string='Army Name', required=True, default='Default Army')
    strength = fields.Float(string='Strength', compute='_compute_attributes', store=True)
    agility = fields.Float(string='Agility', compute='_compute_attributes', store=True)
    pace = fields.Float(string='Pace', compute='_compute_attributes', store=True)
    defence = fields.Float(string='Defence', compute='_compute_attributes', store=True)
    player_id = fields.Many2one('res.partner', string='Player', required=True)
    heroes = fields.Many2many('fifire.hero', string='Heroes', domain="[('player_id', '=', player_id)]")
    tower_id = fields.Many2one('fifire.tower', string='Tower', required=True)
    health = fields.Float(string='Health', default=100)

    @api.depends('heroes.strength', 'heroes.agility', 'heroes.pace', 'heroes.defence', 'health')
    def _compute_attributes(self):
        for army in self:
            total_health_percentage = army.health / 100.0
            army.strength = sum(army.heroes.mapped('strength')) * total_health_percentage
            army.agility = sum(army.heroes.mapped('agility')) * total_health_percentage
            army.pace = sum(army.heroes.mapped('pace')) * total_health_percentage
            army.defence = sum(army.heroes.mapped('defence')) * total_health_percentage

    @api.constrains('player_id', 'tower_id')
    def _check_player_tower_match(self):
        for army in self:
            if army.player_id != army.tower_id.player_id:
                raise ValueError("Player and Tower must belong to the same player.")



class battle(models.Model):
    _name = 'fifire.battle'
    _description = 'Battle in the Game'

    name = fields.Char(string='Battle Name', required=True)
    attacker_id = fields.Many2one('res.partner', string='Attacker', required=True)
    defender_id = fields.Many2one('res.partner', string='Defender', required=True)
    winner_id = fields.Many2one('res.partner', string='Winner', readonly=True)
    status = fields.Selection([('pending', 'Pending'), ('completed', 'Completed'), ('draw', 'Draw')],
                              string='Status', default='pending')
    date_start = fields.Datetime(string='Battle Time')
    chosen_attacker_army_id = fields.Many2one('fifire.army', string='Chosen Attacker Army', required=True)
    chosen_defender_army_id = fields.Many2one('fifire.army', string='Chosen Defender Army', required=True)

    @api.model
    def create(self, values):
        values['date_start'] = values.get('date_start', fields.Datetime.now())
        values['status'] = 'pending'
        return super(battle, self).create(values)

    @api.model
    def simulate_battle(self, cron_mode=True):
        for battle in self.search([('status', '=', 'pending')]):
            attacker_army = battle.chosen_attacker_army_id
            defender_army = battle.chosen_defender_army_id

            attacker_strength = sum(attacker_army.heroes.mapped('strength'))
            defender_strength = sum(defender_army.heroes.mapped('strength'))

            if attacker_strength > defender_strength:
                winner = battle.attacker_id
            elif attacker_strength < defender_strength:
                winner = battle.defender_id
            else:
                winner = None 

            battle.write({
                'winner_id': winner.id if winner else None,
                'status': 'completed' if winner else 'draw',
            })

            battle.handle_battle_outcome()

    def handle_battle_outcome(self):
        if self.winner_id:
            self.winner_id.armies.write({'health': 100})
            self.winner_id.heroes.write({'health': 100})
            self.winner_id.towers.write({'health': 100})
        else:
            pass

    def action_launch_battle_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fifire.battle.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('fifire.view_battle_wizard_form').id,
            'target': 'new',
        }        
    @api.constrains('date_start')
    def _check_date_start(self):
        for battle in self:
            if battle.date_start and battle.date_start <= fields.Datetime.now():
                raise ValidationError("Battle start date must be in the future!")

   

class battlewizard(models.TransientModel):
    _name = 'fifire.battle.wizard'
    _description = 'Battle Wizard'

    name = fields.Char(string='Battle Name', required=True)
    description = fields.Text(string='Description')
    attacker_army_id = fields.Many2one('fifire.army', string='Attacker Army')
    defender_army_id = fields.Many2one('fifire.army', string='Defender Army')
    date_start = fields.Datetime(string='Battle Time')
    total_attacker_strength = fields.Float(string='Total Attacker Strength', readonly=True)
    total_defender_strength = fields.Float(string='Total Defender Strength', readonly=True)
    """state = fields.Char(default='page_1')"""
    state = fields.Selection([
        ('page_1', 'Battle Details'),
        ('page_2', 'Additional Information')
    ], default='page_1')


    """@api.constrains('attacker_army_id', 'defender_army_id')
    def _check_army_players(self):
        for wizard in self:
            if wizard.attacker_army_id.player_id == wizard.defender_army_id.player_id:
                raise exceptions.ValidationError("Attacker y Defender no pueden ser el mismo ejército.")"""

    @api.onchange('attacker_army_id')
    def _onchange_attacker_army_id(self):
        if self.attacker_army_id:
            self.total_attacker_strength = sum(self.attacker_army_id.heroes.mapped('strength'))
        else:
            self.total_attacker_strength = 0.0

    @api.onchange('defender_army_id')
    def _onchange_defender_army_id(self):
        if self.defender_army_id:
            self.total_defender_strength = sum(self.defender_army_id.heroes.mapped('strength'))
        else:
            self.total_defender_strength = 0.0


    def action_next(self):
        if self.state == 'page_1':
            self.state = 'page_2'
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_previous(self):
        if self.state == 'page_2':
            self.state = 'page_1'
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
        

    def action_finish(self):
        Battle = self.env['fifire.battle']
        battle_values = {
            'name': self.name,
            'attacker_id': self.attacker_army_id.player_id.id,
            'defender_id': self.defender_army_id.player_id.id,
            'chosen_attacker_army_id': self.attacker_army_id.id,
            'chosen_defender_army_id': self.defender_army_id.id,
            'date_start': self.date_start
        }
        Battle.create(battle_values)


class recruitwizard(models.TransientModel):
    _name = 'fifire.recruit.wizard'
    _description = 'Recruit Hero Wizard'

    hero_id = fields.Many2one('fifire.hero', string='Select Hero', required=True)
    player_id = fields.Many2one('res.partner', string='Player', required=True)

    @api.onchange('hero_id')
    def _onchange_hero_id(self):
        if self.hero_id and self.hero_id.player_id:
            self.player_id = self.hero_id.player_id.id

    def recruit_hero(self):
        self.ensure_one()
        hero = self.hero_id
        player = self.player_id
        if hero and player:
            if hero.player_id:
                raise ValueError("This hero already belongs to a player.")

            hero.write({'player_id': player.id})
        else:
            raise ValueError("Please select both a hero and a player.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Recruited Hero',
            'res_model': 'fifire.hero',
            'view_mode': 'form',
            'res_id': hero.id,
            'target': 'current',
        }
