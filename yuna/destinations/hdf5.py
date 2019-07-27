from datetime import datetime
try:
    import h5py
except ImportError:
    pass
import numpy
from . import logger
from yuna.core import DestinationSingleton, Truck, Plane, SourceSingleton


class Hdf5Destination(DestinationSingleton):

    def call_to_destination(self):
        pass

    def unpacking(self, plane):
        """
        当truck不存在任何字段时，从truck获取到的数据内容如下：
        code = ["None"]，pe = [0], pb = [0], ps = [0], pcf = [0], time = [datetime(2000, 1, 1)],
        low = [0], high = [0], close = [0], volume = [0]

        :param plane: 即将要卸货装载着多个truck的plane实例
        """

        with h5py.File("data.hdf5", 'a') as file:
            for truck in plane:
                code = truck.get("Code", "None")
                if code is 'None':
                    continue
                pe = truck.get("PE", [0])
                pb = truck.get("PB", [0])
                ps = truck.get("PS", [0])
                pcf = truck.get("PCF", [0])
                time = truck.get("Times", [datetime(2000, 1, 1)])
                low = truck.get("Low", [0])
                high = truck.get("High", [0])
                close = truck.get("Close", [0])
                volume = truck.get("Volume", [0])
                g = file.create_group(code[0])
                temp = numpy.array(code)
                ds = g.create_dataset("Code", temp.shape, dtype=h5py.special_dtype(vlen=str))
                ds[...] = temp
                temp = numpy.array(pe)
                ds = g.create_dataset("PE", temp.shape, float)
                ds[...] = temp
                temp = numpy.array(pb)
                ds = g.create_dataset("PB", temp.shape, float)
                ds[...] = temp
                temp = numpy.array(ps)
                ds = g.create_dataset("PS", temp.shape, float)
                ds[...] = temp
                temp = numpy.array(pcf)
                ds = g.create_dataset("PCF", temp.shape, float)
                ds[...] = temp
                temp = numpy.array(list(map(lambda x: x.strftime("%Y%m%d"), time)))
                ds = g.create_dataset("Times", temp.shape, dtype=h5py.special_dtype(vlen=str))
                ds[...] = temp
                temp = numpy.array(low)
                ds = g.create_dataset("Low", temp.shape, float)
                ds[...] = temp
                temp = numpy.array(high)
                ds = g.create_dataset("High", temp.shape, float)
                ds[...] = temp
                temp = numpy.array(close)
                ds = g.create_dataset("Close", temp.shape, float)
                ds[...] = temp
                temp = numpy.array(volume)
                ds = g.create_dataset("Volume", temp.shape, float)
                ds[...] = temp
                logger.debug(truck.get("Code", "None"))

    def sold_out(self):
        pass

    def find_out(self, stocks, from_query_date, to_query_date):
        plane = Plane()
        with h5py.File("data.hdf5", 'r') as file:
            for stock in stocks:
                stock = SourceSingleton.alter_stock_code(stock)
                g = file.get(stock)
                time_array = g.get('Times')[...].tolist()
                if from_query_date is not None:
                    if to_query_date is not None:
                        for i in time_array:
                            if i >= from_query_date:
                                from_index = time_array.index(i)
                                break
                        if from_query_date < to_query_date:
                            for i in time_array[from_index:]:
                                if i >= to_query_date:
                                    to_index = time_array.index(i)
                                    break
                                else:
                                    to_index = None
                        else:
                            raise Exception
                    else:
                        for i in time_array:
                            if i >= from_query_date:
                                from_index = time_array.index(i)
                                to_index = None
                                break
                else:
                    from_index = None
                    to_index = None
                truck = Truck()
                truck.append('Code', g.get('Code')[...][0])
                truck.append('PE', g.get('PE')[...][0])
                truck.append('PB', g.get('PB')[...][0])
                truck.append('PS', g.get('PS')[...][0])
                truck.append('PCF', g.get('PCF')[...][0])
                truck.extend('Times', list(map(lambda x: datetime.strptime(x, "%Y%m%d"), time_array[from_index:to_index])))
                truck.extend('Low', g.get('Low')[...].tolist()[from_index:to_index])
                truck.extend('High', g.get('High')[...].tolist()[from_index:to_index])
                truck.extend('Close', g.get('Close')[...].tolist()[from_index:to_index])
                truck.extend('Volume', g.get('Volume')[...].tolist()[from_index:to_index])
                plane.append(truck)
        return plane
