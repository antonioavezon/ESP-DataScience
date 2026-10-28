## Inicio

cd /home/antonio/projects/HUC/HUC-1.0.0
./iniciar.sh

## Inicio con GPU

cd /home/antonio/projects/HUC/HUC-1.0.0
./iniciar.sh gpu

## Detención

cd /home/antonio/projects/HUC/HUC-1.0.0
./detener.sh

## Estado

cd /home/antonio/projects/HUC/HUC-1.0.0
./estado.sh

## Logs

cd /home/antonio/projects/HUC/HUC-1.0.0
docker compose logs

## Fórmulas

cd /home/antonio/projects/HUC/HUC-1.0.0
docker compose exec huc-proceso python /app/proceso/formulas.py list

## Visualizador

cd /home/antonio/projects/HUC/HUC-1.0.0
./estado.sh
hostname -I

http://IP_DEL_PC:8000

## Simulador

http://IP_DEL_PC:8001
