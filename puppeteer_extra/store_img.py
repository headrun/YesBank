import base64
import re
import os
import MySQLdb


class StoreImg():
    """ Storing images in local """

    def __init__(self):
        """ Initialising MySQL Connections """

        self.conn = MySQLdb.connect(db='yesbank', host='localhost', user='yesbank',
                                    passwd='y@sbankh@adrun', charset="utf8", use_unicode=True)
        self.cur = self.conn.cursor()

    def __del__(self):
        """ Closing Connections """

        self.cur.close()
        self.conn.close()

    def main(self):
        """ Convert base64 to image format and store the image """

        query = "select keyword, logo_url from right_side_data where \
                logo_url != '' and saved_logo = 0"
        self.cur.execute(query)
        data = self.cur.fetchall()
        for dat in data:
            import pdb;pdb.set_trace()
            keyword, logo_url = dat
            file_type, logo = logo_url.split(',')
            img_ext = re.findall('/(.*);', file_type)[0]
            img_ext = img_ext if img_ext.strip() else 'png'
            cur_dir = os.getcwd()
            img_dir = os.path.join(cur_dir, r'images')
            if not os.path.exists(img_dir):
                os.makedirs(img_dir)
            with open(img_dir + '/' + keyword + "." + img_ext, "wb") as fh:
                fh.write(base64.urlsafe_b64decode(logo))
            print('Image Saved '+ keyword)
            self.cur.execute("update right_side_data set saved_logo = 1 where keyword = '{0}' \
                and logo_url = '{1}'".format(keyword, logo_url))
            self.conn.commit()

if __name__ == '__main__':
    OBJ = StoreImg()
    OBJ.main()
