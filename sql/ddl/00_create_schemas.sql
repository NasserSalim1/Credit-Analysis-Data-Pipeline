-- Cria as schemas para as camadas do Data Warehouse

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS trusted;
CREATE SCHEMA IF NOT EXISTS refined;

COMMENT ON SCHEMA raw IS 'Camada RAW (Bronze): Dados brutos preservados como recebidos';
COMMENT ON SCHEMA trusted IS 'Camada TRUSTED (Silver): Dados limpos e integrados - Single Source of Truth';
COMMENT ON SCHEMA refined IS 'Camada REFINED (Gold): Modelo dimensional para análises e BI';