import flask as fl
import flask_sqlalchemy as fls
import os

app = fl.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbase.db'
app.config.update(SECRET_KEY=os.urandom(24))
db = fls.SQLAlchemy(app)

connector_dict = {
    'Быть видом': 'Иметь вид',
    'Выбирает': 'Выбран',
    'Нанимает': 'Нанят',
    'Предоставляет': 'Предоставлен',
    'Продаваться в': 'Продавать'
}
shape_dict = {
    'Покупатель': 'Человек, который нуждается в покупке',
    'Служба доставки': 'Доставляет покупку из магазина',
    'Напольное покрытие': 'Товар, который приобретает покупатель',
    'Паркет': 'Вид покрытия',
    'Линолеум': 'Вид покрытия',
    'Ламинат': 'Вид покрытия',
    'Магазин': 'Место, в котором совершается покупка',
    'Мастер': 'Устанавливает приобретенный товар',
    'Магазин стройматериалов': 'Продает вспомогательные вещи',
    'Плитка': 'Вид покрытия'
}


class Shape(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Shape %r>' % self.id


class Connector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    source_id = db.Column(db.Integer)
    target_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Group %r>' % self.id


@app.route('/')
def index():
    return fl.redirect('/table')


@app.route('/table', methods=['POST', 'GET'])
def table():
    shapes = Shape.query.all()
    if fl.request.method == 'POST':

        for el in shapes:
            db.session.delete(el)

        connectors = Connector.query.all()
        for el in connectors:
            db.session.delete(el)

        db.session.commit()

        file = fl.request.files['file'].read().decode('utf-8')
        file = file.split('\n')
        id, name, flag = 0, '', 0

        for line in file:
            line = str(line)
            if flag:
                source_id = int(line[line.index('source="') + 8:line.index('" target')])
                target_id = int(line[line.index('target="') + 8:line.index('"', line.index('target="') + 8)])
                connector = Connector(id=id, name=name, source_id=source_id, target_id=target_id)
                db.session.add(connector)
                flag = 0
            if line.find('<Shape') != -1:
                id = int(line[line.index('id="') + 4:line.index('">')])
                name = line[line.index('label="') + 7:line.index('" href')]
                desc = ''
                if name in shape_dict:
                    desc = shape_dict[name]
                shape = Shape(id=id, name=name, desc=desc)
                db.session.add(shape)
            if line.find('<Connector') != -1:
                id = int(line[line.index('id="') + 4:line.index('">')])
                name = line[line.index('label="') + 7:line.index('" href')]
                flag = 1

        connectors = Connector.query.all()
        for el in connectors:
            if el.name in connector_dict:
                connector = Connector(name=connector_dict[el.name], source_id=el.target_id, target_id=el.source_id)
                db.session.add(connector)

        db.session.commit()

        return fl.redirect('/table')
    else:
        return fl.render_template('table.html', list=shapes)


@app.route('/table/<int:id>')
def shape_view(id):
    shape = Shape.query.get(id)
    connects = Connector.query.filter_by(source_id=shape.id)
    list = []
    for con in connects:
        list.append([shape, con, Shape.query.filter_by(id=con.target_id).first()])
    return fl.render_template('view.html', list=list)


@app.route('/table/desc/<int:id>', methods=['POST', 'GET'])
def shape_desc(id):
    shape = Shape.query.get(id)
    if fl.request.method == 'POST':
        desc = fl.request.form['desc']
        shape.desc = desc
        db.session.commit()
        return fl.redirect('/table')
    else:
        return fl.render_template('desc.html', ph=shape.desc)


@app.route('/table/create_shape', methods=['POST', 'GET'])
def create_shape():
    if fl.request.method == 'POST':
        name = fl.request.form['name']
        desc = fl.request.form['description']
        shape = Shape(name=name, desc=desc)
        db.session.add(shape)
        db.session.commit()
        return fl.redirect('/table')
    else:
        form = ['name', 'description']
        return fl.render_template('screate.html', form=form)


@app.route('/table/create_connector', methods=['POST', 'GET'])
def create_connector():
    if fl.request.method == 'POST':
        name = fl.request.form['name']
        source = int(fl.request.form['source'])
        target = int(fl.request.form['target'])
        connector = Connector(name=name, source_id=source, target_id=target)
        db.session.add(connector)
        if connector.name in connector_dict:
            connector = Connector(name=connector_dict[name], source_id=source, target_id=target)
            db.session.add(connector)
        db.session.commit()
        return fl.redirect('/table')
    else:
        shapes = Shape.query.all()
        return fl.render_template('ccreate.html', shapes=shapes)


@app.route('/table/<int:id>/update/<int:id2>', methods=['POST', 'GET'])
def update_con(id, id2):
    connector = Connector.query.get(id2)
    if fl.request.method == 'POST':
        name = fl.request.form['name']
        connector.name = name
        db.session.commit()
        return fl.redirect('/table/' + str(id))
    else:
        return fl.render_template('update.html', ph=connector.name, id=id)


if __name__ == '__main__':
    app.run(debug=True)
