HORIZONTAL_TABLE = b'\x09'


class SampleFlagInfo(object):
    def __init__(self, sample_id, flag, time_stamp, descrip=''):
        self.sample_id = sample_id
        self.flag = flag
        self.time_stamp = time_stamp
        self.Description = descrip

    def __str__(self):
        return "sample id:" + str(self.sample_id) + HORIZONTAL_TABLE +\
            "sample flag:" + str(self.flag) + HORIZONTAL_TABLE +\
            "time stamp:" + str(self.time_stamp) + HORIZONTAL_TABLE +\
            "description:" + str(self.Description)


if __name__ == "__main__":
    sample1 = SampleFlagInfo(1234,"A","20151221115948")
    sample2 = SampleFlagInfo(4567,"B","19881221115948",'inlabbed from column B of rack 4567')

    print sample1
    print sample2
