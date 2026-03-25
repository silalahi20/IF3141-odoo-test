from odoo import models, fields

class Produk(models.Model):
    _name = 'toko.produk'
    _description = 'Produk Toko'

    name = fields.Char(string='Nama Produk', required=True)
    harga = fields.Float(string='Harga')
    stok = fields.Integer(string='Stok')
    deskripsi = fields.Text(string='Deskripsi')