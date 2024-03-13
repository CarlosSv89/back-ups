from odoo import models, fields, api


class pos_price_list(models.Model):
  _name = 'product.pricelist' # Model name
  _inherit = ['product.pricelist', 'mail.thread', 'mail.activity.mixin'] # Inherit from product.pricelist
  
  
  # Tracking fields
  name = fields.Char(tracking=True)
  currency_id = fields.Many2one(tracking=True)
  company_id = fields.Many2one(tracking=True)
  
  
  item_ids = fields.One2many(comodel_name='product.pricelist.item', inverse_name='pricelist_id', tracking=True)
  
  
  # Compare initial_values and new_values
  def compare_items(self, initial_values, new_values):
    changes = [] # List to store changes
    for initial, new in zip(initial_values, new_values):
      # for key in initial:
      if initial != new: # If the value has changed store it with a format
        # IVA
        iva = None
        if new['applied_on'] in ['3_global', '2_product_category']:
          iva = f"IVA: {new['iva_precio']}"
        else:
          iva = 'IVA: N/A'
        old_val = f"- Nombre: {initial['name']}, Cantidad mínima: {initial['min_quantity']}, Precio: {initial['price']}, Fecha de inicio: {initial['date_start']}, Fecha de fin: {initial['date_end']}, Comision: {initial['comision']}, Comision acumulada: {initial['comision_acumulada']}, Descuento: {initial['descuento']}, Subsidio: {initial['subsidio']}, DIP: {initial['dip']}, IVA: {initial['iva_precio']}"
        new_val = f"- Nombre: {new['name']}, Cantidad mínima: {new['min_quantity']}, Precio: {new['price']}, Fecha de inicio: {new['date_start']}, Fecha de fin: {new['date_end']}, Comision: {new['comision']}, Comision acumulada: {new['comision_acumulada']}, Descuento: {new['descuento']}, Subsidio: {new['subsidio']}, DIP: {new['dip']}, {iva}"
        changes.append((old_val, new_val))
    return changes
    
  # Method to track changes on item_ids
  def write(self, vals):
    if 'item_ids' in vals:
      for record in self:
        # Initial values to compare
        initial_values = [{
          'name': rec.name, 
          'min_quantity':rec.min_quantity, 
          "price":rec.price, 
          'date_start':rec.date_start, 
          'date_end':rec.date_end, 
          'comision':rec.comision, 
          'comision_acumulada':rec.comision_acumulada, 
          'descuento': rec.descuento, 
          'subsidio':rec.subsidio, 
          'dip': rec.dip, 
          'iva_precio': rec.iva_precio, 
          'applied_on': rec.applied_on
        } for rec in record.item_ids ]
        initial_value = ''.join(f"- Nombre: {rec.name}, Cantidad minima: {rec.min_quantity}, Precio: {rec.price}, Fecha inicio: {rec.date_start}, Fecha final: {rec.date_end}, Comision: {rec.comision}, Comision acumulada: {rec.comision_acumulada}, Descuento: {rec.descuento}, Subsidio: {rec.subsidio}, DIP: {rec.dip},  IVA: {rec.iva_precio if rec.applied_on in ['3_global', '2_product_category'] else 'N/A'} <br/>" for rec in record.item_ids)
        init_size = len(record.item_ids)
        
        # super need to be before new_value
        result = super().write(vals) 
        
        # New values to compare
        new_value = ''.join(f"- Nombre: {rec.name}, Cantidad minima: {rec.min_quantity}, Precio: {rec.price}, Fecha inicio: {rec.date_start}, Fecha final: {rec.date_end}, Comision: {rec.comision}, Comision acumulada: {rec.comision_acumulada}, Descuento: {rec.descuento}, Subsidio: {rec.subsidio}, DIP: {rec.dip}, IVA: {rec.iva_precio if rec.applied_on in ['3_global', '2_product_category'] else 'N/A'}<br/>" for rec in record.item_ids)
        new_values = [{
          'name': rec.name, 
          'min_quantity':rec.min_quantity, 
          "price":rec.price, 
          'date_start':rec.date_start, 
          'date_end':rec.date_end, 
          'comision':rec.comision, 
          'comision_acumulada':rec.comision_acumulada, 
          'descuento': rec.descuento, 
          'subsidio':rec.subsidio, 
          'dip': rec.dip, 
          'iva_precio': rec.iva_precio,
          'applied_on': rec.applied_on
        } for rec in record.item_ids]
        new_size = len(record.item_ids)
        last_item = None
        
        # validate if there is a new item
        if new_size > 0:
          iva = None
          if record.item_ids[new_size - 1].applied_on in ['3_global', '2_product_category']:
            iva = f"IVA: {record.item_ids[new_size - 1].iva_precio}" 
          else:
            iva = 'IVA: N/A'           
          last_item = f"- Nombre: {record.item_ids[new_size - 1].name}, Cantidad minima: {record.item_ids[new_size - 1].min_quantity}, Precio: {record.item_ids[new_size - 1].price}, Fecha inicio: {record.item_ids[new_size - 1].date_start}, Fecha final: {record.item_ids[new_size - 1].date_end}, Comision: {record.item_ids[new_size - 1].comision}, Comision acumulada: {record.item_ids[new_size - 1].comision_acumulada}, Descuento: {record.item_ids[new_size - 1].descuento}, Subsidio: {record.item_ids[new_size - 1].subsidio}, DIP: {record.item_ids[new_size - 1].dip}, {iva}"
          
        # String formatted to log when an item has changed 
        message_body = self.compare_items(initial_values, new_values)
        
        # if a new item is added
        if init_size < new_size:
          if init_size == 0:
            body = f"Se agregaron estas normas: <br/> {new_value}"
            record.message_post(body=body)
          else:
            body = f"Se creo una norma: <br/> {last_item}"
            record.message_post(body=body)
        # if an item is deleted
        elif init_size > new_size:
          body = f"Se eliminaron normas: <br/> <strong>Antes:</strong> <br/> {initial_value}<br/><br/> <strong>Resultado:</strong><br/> {new_value}"
          record.message_post(body=body)
        # if an item is modified 
        else: 
          if initial_value != new_value:
            for message in message_body:
              record.message_post(body=f"Se modifico una norma: <br/> <strong>Antes:</strong> <br/>{message[0]}<br/><br/>  <strong>Resultado:</strong><br/> {message[1]}")
        return result
    else:
      return super().write(vals)