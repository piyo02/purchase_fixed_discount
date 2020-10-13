from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    amount_discount_fixed = fields.Monetary(string='Total Discount', store=True, readonly=True, compute='_amount_all')

    @api.depends('order_line.price_total')
    def _amount_all(self):
        vals = {}
        amount_discount_fixed = 0
        for line in self.mapped('order_line').filtered(
                lambda l: l.discount_fixed):
            vals[line] = {
                'price_unit': line.price_unit,
                'discount_fixed': line.discount_fixed,
            }
            price_unit = line.price_unit - line.discount_fixed
            amount_discount_fixed += line.discount_fixed*line.product_qty
            line.update({
                'price_unit': price_unit,
                'discount_fixed': 0.0,
            })
            line.order_id.update({
                'amount_discount_fixed': amount_discount_fixed
            })
        res = super(PurchaseOrder, self)._amount_all()
        for line in vals.keys():
            line.update(vals[line])
        return res

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits=dp.get_precision('Discount'),
        help="Fixed amount discount.")

    @api.onchange('discount_fixed')
    def _get_discounted_price_unit(self):
        price_unit = super(
            PurchaseOrderLine, self)._get_discounted_price_unit()
        if self.discount_fixed:
            price_unit -= self.discount_fixed
        return price_unit

    @api.onchange('discount_fixed')
    def _use_discount_fixed(self):
        if self.discount_fixed:
            self.discount = 0.0
            self.discount2 = 0.0
            self.discount3 = 0.0

    @api.onchange('discount', 'discount2', 'discount3')
    # @api.onchange('discount')
    def _onchange_discount(self):
        if self.discount or self.discount2 or self.discount3:
        # if self.discount:
            self.discount_fixed = 0.0

    @api.one
    @api.constrains('discount', 'discount_fixed')
    def _check_only_one_discount(self):
        if self.discount and self.discount_fixed:
            raise ValidationError(
                _("You can only set one type of discount per line."))

    @api.depends('discount_fixed')
    def _compute_amount(self):
        vals = {}
        for line in self.filtered(lambda l: l.discount_fixed):
            vals[line] = {
                'price_unit': line.price_unit,
                'discount_fixed': line.discount_fixed,
            }
            price_unit = line.price_unit - line.discount_fixed
            line.update({
                'price_unit': price_unit,
                'discount_fixed': 0.0,
            })
        res = super(PurchaseOrderLine, self)._compute_amount()
        for line in vals.keys():
            line.update(vals[line])
        return res