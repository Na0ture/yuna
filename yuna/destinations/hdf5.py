from datetime import datetime
import h5py
import numpy
from yuna.core import DestinationSingleton, Truck, Plane, SourceSingleton


class Hdf5Destination(DestinationSingleton):

    def call_to_destination(self):
        pass

    def unpacking(self, plane):

        with h5py.File("data.hdf5", 'a') as file:
            self.z = 0
            for truck in plane:
                code = truck.get("Code", "None")[0]
                if code is 'None':
                    continue
                pe = truck.get("PE", [0])[0]
                pb = truck.get("PB", [0])[0]
                ps = truck.get("PS", [0])[0]
                pcf = truck.get("PCF", [0])[0]
                time = truck.get("Times", [datetime(2000, 1, 1)])
                low = truck.get("Low", [0])
                high = truck.get("High", [0])
                close = truck.get("Close", [0])
                volume = truck.get("Volume", [0])

                g = file.create_group(code)

                temp = numpy.array([code])
                ds = g.create_dataset("Code", temp.shape, dtype=h5py.special_dtype(vlen=str))
                ds[...] = temp

                temp = numpy.array([pe])
                ds = g.create_dataset("PE", temp.shape, float)
                ds[...] = temp

                temp = numpy.array([pb])
                ds = g.create_dataset("PB", temp.shape, float)
                ds[...] = temp

                temp = numpy.array([ps])
                ds = g.create_dataset("PS", temp.shape, float)
                ds[...] = temp

                temp = numpy.array([pcf])
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
                self.z += 1
                print(self.z)

    def sold_out(self):
        pass

    def find_out(self, stocks):
        plane = Plane()
        stocks = SourceSingleton.change_stock(stocks)
        with h5py.File("data.hdf5", 'r') as file:
            for stock in stocks:
                truck = Truck()
                g = file.get(stock)

                truck.append('Code', g.get('Code')[...][0])
                truck.append('PE', g.get('PE')[...][0])
                truck.append('PB', g.get('PB')[...][0])
                truck.append('PS', g.get('PS')[...][0])
                truck.append('PCF', g.get('PCF')[...][0])
                truck.extend('Times', list(map(lambda x: datetime.strptime(x, "%Y%m%d"), g.get('Times')[...].tolist())))
                truck.extend('Low', g.get('Low')[...].tolist())
                truck.extend('High', g.get('High')[...].tolist())
                truck.extend('Close', g.get('Close')[...].tolist())
                truck.extend('Volume', g.get('Volume')[...].tolist())
                plane.append(truck)
        return plane
