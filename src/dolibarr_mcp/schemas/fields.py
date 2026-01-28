"""Field definitions for response filtering.

These define which fields to include when returning entity data,
reducing token usage by excluding unnecessary fields.
"""

from typing import List

# =============================================================================
# ENTITY FIELD FILTERS
# =============================================================================

CUSTOMER_FIELDS: List[str] = [
    "id",
    "name",
    "name_alias",
    "email",
    "phone",
    "address",
    "town",
    "zip",
    "country_code",
    "client",
    "fournisseur",
    "code_client",
    "status",
]

PRODUCT_FIELDS: List[str] = [
    "id",
    "ref",
    "label",
    "description",
    "price",
    "price_ttc",
    "type",
    "status",
    "stock_reel",
    "barcode",
]

INVOICE_FIELDS: List[str] = [
    "id",
    "ref",
    "socid",
    "date",
    "date_lim_reglement",
    "total_ht",
    "total_tva",
    "total_ttc",
    "paye",
    "status",
    "lines",
]

ORDER_FIELDS: List[str] = [
    "id",
    "ref",
    "socid",
    "date",
    "total_ht",
    "total_ttc",
    "status",
    "lines",
]

PROPOSAL_FIELDS: List[str] = [
    "id",
    "ref",
    "socid",
    "date",
    "fin_validite",
    "total_ht",
    "total_tva",
    "total_ttc",
    "status",
    "lines",
]

PROJECT_FIELDS: List[str] = [
    "id",
    "ref",
    "title",
    "description",
    "socid",
    "status",
    "date_start",
    "date_end",
]

CONTACT_FIELDS: List[str] = [
    "id",
    "firstname",
    "lastname",
    "email",
    "phone",
    "socid",
]

USER_FIELDS: List[str] = [
    "id",
    "login",
    "lastname",
    "firstname",
    "email",
    "admin",
    "status",
]

LINE_FIELDS: List[str] = [
    "id",
    "fk_product",
    "desc",
    "qty",
    "subprice",
    "total_ht",
    "total_ttc",
    "tva_tx",
]

# =============================================================================
# FIELD GROUPS BY OPERATION TYPE
# =============================================================================

# Minimal fields for list operations (to save tokens)
CUSTOMER_LIST_FIELDS: List[str] = ["id", "name", "email", "phone", "status"]
PRODUCT_LIST_FIELDS: List[str] = ["id", "ref", "label", "price", "status"]
INVOICE_LIST_FIELDS: List[str] = ["id", "ref", "socid", "total_ttc", "status"]

# Expanded fields for detail operations
CUSTOMER_DETAIL_FIELDS: List[str] = CUSTOMER_FIELDS + ["date_creation", "date_modification"]
PRODUCT_DETAIL_FIELDS: List[str] = PRODUCT_FIELDS + ["tva_tx", "weight", "volume"]
