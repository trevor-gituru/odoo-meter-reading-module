sudo apt install -y git python3-pip python3-venv python3-dev \
build-essential libxml2-dev libxslt1-dev zlib1g-dev \
libsasl2-dev libldap2-dev libjpeg-dev libpq-dev \
libffi-dev libssl-dev node-less npm postgresql

git clone https://github.com/odoo/odoo.git --depth 1 --branch 18.0
cd odoo

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip wheel
pip install -r requirements.txt

sudo -u postgres psql
CREATE USER odoo WITH PASSWORD 'odoo';
ALTER USER odoo CREATEDB;
\q

mkdir custom_addons
cat odoo.conf
[options]
addons_path = addons,custom_addons
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
#start odoo
python3 odoo-bin -c odoo.conf

# add module 
./odoo-bin scaffold meter_invoice custom_addons

# Update module
python3 odoo-bin -c odoo.conf -u meter_invoice -d meter_invoice_dev


## Web
-> Setup master db
- Enable developer mode (app - settings)

