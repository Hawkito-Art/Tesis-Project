# Tablas que va a menejar el programa

## Tabla ejemplo para guardar en la base de datos 
|                                    |      | PLAN     | Año Anter  |            | ACUMULADO  |       | Por ciento  | Estimado   | Estimado        |
|------------------------------------|------|----------|------------|------------|------------|-------|-------------|------------|-----------------|
| INDICADORES                        | U:M  | AÑO      |            | PLAN       | REAL       | R/P   | R/AA        | próx. mes  | cierre del año  |
| Ventas Totales                     | MP   | 145881.2 | 100209.3   | 145,881.2  | 121,785.0  | 83.5  | 102.3       | 10764.9    | 145881.2        |
| Total de Ingresos                  | MP   | 154758.3 | 98,682.10  | 154,758.30 | 123,969.2  | 80.1  | 107.0       | 11542.2    | 154758.3        |
| Total de Gastos                    | MP   | 149395.7 | 100,876.90 | 149,395.70 | 124,442.60 | 83.3  | 105.0       | 11120.3    | 149395.7        |
| Utilidad                           | MP   | 5362.6   | 2,194.80   | 5362.6     | 473.4      | 8.8   | 14.0        | 421.9      | 5362.6          |
| Indicadores Limites                |      |          |            |            |            |       |             |            |                 |
| Gasto de Salario x peso V.A.       | peso | 1.1206   | 0.9541     | 1.1206     | 0.7354     | 65.6  | 76.7        | 5412.0000  | 1.1206          |
| Otros Indicadores                  |      |          |            |            |            |       |             |            |                 |
| Gasto ToTal x peso de ing.Tot      | peso | 0.9653   | 1.0222     | 0.9653     | 1.0038     | 104.0 | 98.1        | 0.9634     | 0.9653          |
| Valor Agregado Bruto               | U    | 11786.0  | 7,337.10   | 11,786.00  | 10,357.70  | 87.9  | 119.7       | 2033.60    | 11786           |
| Utilidad Antes  Imp. x $ de VAB    | peso | 0.4550   | 0.2991     | 0.4550     | 0.0457     | 10.0  | 11.7        | 0.2075     | 0.455           |
| Fondo de Salario Total             | MP   | 13207.1  | 7,000.50   | 13,207.10  | 7,617.50   | 57.7  | 91.8        | 1100.60    | 13207.1         |
| Promedio de Trabajadores           | U    | 269      | 240        | 269        | 213        | 79.2  | 90.0        | 269        | 269             |
| Productividad del Trabajo          | p    | 43815.00 | 30,571.00  | 43,815.00  | 48,628.00  | 111.0 | 133.0       | 7560.00    | 43815           |
| Salario Medio                      | p    | 4091.00  | 2,917.00   | 4091.00    | 2980.00    | 72.8  | 102.0       | 4091.00    | 4091            |
| Correlación Salario Medio/Product. | Coef |          |            |            |            |       |             |            |                 |

Las tablas manejadas tienen ese modelo y formato
Los indicadores y columnas siempre son esas 

## Calculos
Las columnas Plan, Anho anterior las ingresa el usuario manualmente 
Las columnas Plan y real tambien ya estan previamente introducidas

La columna de R/P se calcula el valor real/plan*100, ejemplo en la fila de ventas totales 	121,785.0/ 	145,881.2 * 100 dando su respectivo valor 

La columna R/AA se calcula el valor real/anho anterior *100, ejemplo en la fila de ventas totales 121,785.0/100209.3 * 100 dando su respectivo valor 

La columna estimado proximo mes se calcula el valor real + (el valor real * 0.1), ejemplo en la fila de ventas totales 121,785.0 + ( 121,785.0 * 0.1) dando su respectivo valor

La fila de Correlación Salario Medio/Product. se va calculando el valor de fila superior Salario Medio/Productividad del Trabajo, ejemplo en Plan Anho 	4091.00/ 43815.00