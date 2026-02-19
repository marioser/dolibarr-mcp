# Dolibarr MCP - Instrucciones para Agentes IA

## Reglas Importantes

1. **NUNCA uses `dolibarr_raw_api`** para consultas comunes. Usa los tools específicos.
2. **NUNCA inventes nombres de columnas SQL**. Los tools ya tienen los filtros correctos.
3. **Usa `socid`** para filtros de consulta (`get_customer_*`). Para creación de propuesta usa `customer_id` en `create_proposal` (el servidor lo mapea a `socid`).

---

## Propuestas/Ofertas (Proposals)

### Estados de propuestas
| Código | Estado | Descripción |
|--------|--------|-------------|
| 0 | draft | Borrador |
| 1 | validated | Validada/Abierta |
| 2 | signed | Firmada/Ganada |
| 3 | refused | Rechazada/Perdida |

### Consultas comunes

**Últimas N propuestas de un cliente:**
```
get_customer_proposals(socid=542, limit=5)
```

**Propuestas abiertas (borrador + validadas) de un cliente:**
```
get_customer_proposals(socid=542, statuses=[0,1])
```
o
```
get_customer_proposals(socid=542, include_draft=true, include_validated=true)
```

**Propuestas ganadas de un cliente:**
```
get_customer_proposals(socid=542, status=2)
```
o
```
get_customer_proposals(socid=542, include_signed=true)
```

**Propuestas perdidas de un cliente:**
```
get_customer_proposals(socid=542, status=3)
```
o
```
get_customer_proposals(socid=542, include_refused=true)
```

**Propuestas de un año específico:**
```
get_customer_proposals(socid=542, year=2026)
```

**Propuestas de un mes específico:**
```
get_customer_proposals(socid=542, year=2026, month=1)
```

**Buscar propuesta por referencia:**
```
search_proposals(query="OF26012770")
```

**Obtener propuesta específica por ID:**
```
get_proposal_by_id(proposal_id=3183)
```

### Crear propuestas correctamente

**Crear propuesta mínima (recomendado):**
```
create_proposal(customer_id=542, lines=[{"desc":"Servicio","qty":1,"subprice":100}])
```

**Con notas y validez:**
```
create_proposal(
  customer_id=542,
  duree_validite=30,
  note_public="Oferta válida por 30 días",
  note_private="Seguimiento comercial",
  lines=[{"desc":"Consultoría","qty":2,"subprice":150}]
)
```

Notas:
- `customer_id` es el campo esperado por el tool de creación.
- Internamente se transforma a `socid` para Dolibarr.
- Evita `dolibarr_raw_api` para `POST /proposals` salvo casos avanzados de diagnóstico.

---

## Facturas (Invoices)

### Estados de facturas
- `draft` - Borrador
- `unpaid` - No pagada
- `paid` - Pagada

### Consultas comunes

**Últimas facturas de un cliente:**
```
get_customer_invoices(socid=542, limit=5)
```

**Facturas pendientes de pago de un cliente:**
```
get_customer_invoices(socid=542, status="unpaid")
```

**Facturas de un año/mes:**
```
get_customer_invoices(socid=542, year=2026, month=1)
```

---

## Pedidos (Orders)

### Consultas comunes

**Últimos pedidos de un cliente:**
```
get_customer_orders(socid=542, limit=5)
```

**Pedidos de un año/mes:**
```
get_customer_orders(socid=542, year=2026, month=1)
```

---

## Parámetros comunes

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `socid` | int | ID del cliente (thirdparty) |
| `limit` | int | Máximo de resultados (default: 10-50) |
| `year` | int | Filtrar por año (ej: 2026) |
| `month` | int | Filtrar por mes (1-12), requiere year |
| `status` | int/str | Filtrar por estado único |
| `statuses` | [int] | Filtrar por múltiples estados |
| `sortorder` | str | "ASC" o "DESC" (default: DESC) |
| `date_start` | str | Fecha inicio "YYYY-MM-DD" |
| `date_end` | str | Fecha fin "YYYY-MM-DD" |

---

## Errores comunes a evitar

### ❌ INCORRECTO - Usar dolibarr_raw_api con SQL incorrecto
```
dolibarr_raw_api(method="GET", endpoint="/proposals", params={"sqlfilters": "(t.socid:=:542)"})
```
El campo correcto es `t.fk_soc`, no `t.socid`.

### ✅ CORRECTO - Usar el tool específico
```
get_customer_proposals(socid=542)
```

### ❌ INCORRECTO - Buscar por nombre de cliente
```
search_proposals(query="ULTRACEM")  # No funciona para nombres de cliente
```

### ✅ CORRECTO - Primero buscar el cliente, luego sus propuestas
```
search_customers(query="ULTRACEM")  # Obtener socid
get_customer_proposals(socid=542)    # Usar el socid obtenido
```

---

## Flujo recomendado

1. **Identificar el cliente** → `search_customers(query="nombre")` → obtener `socid`
2. **Consultar datos** → usar `get_customer_*` con el `socid`
3. **Filtrar por fecha/estado** → añadir `year`, `month`, `status`, etc.
