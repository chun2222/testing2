def create_classes(db):
    class Breweries(db.Model):
        __tablename__ = 'breweries'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.Integer)        
        brewery_type = db.Column(db.String(256))
        address = db.Column(db.String(256))
        state = db.Column(db.String(256))
        phone = db.Column(db.String(256))
        website_url = db.Column(db.String(256))
        country = db.Column(db.String(256))
        region = db.Column(db.String(256))
        division = db.Column(db.String(256))

        def __repr__(self):
            return f'<Breweries {self.id}>'

    return Breweries
