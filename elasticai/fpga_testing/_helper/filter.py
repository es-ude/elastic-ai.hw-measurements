import numpy as np
import scipy.signal as scft


class FilterElement:
    __filt_btype_dict: dict = {
        "low": "lowpass",
        "high": "highpass",
        "bandpass": "bandpass",
        "bandstop": "bandstop",
        "all": "allpass",
    }
    __filt_ftype_dict: dict = {
        "butter": "butter",
        "cheby1": "cheby1",
        "cheby2": "cheby2",
        "ellip": "ellip",
        "bessel": "bessel",
    }
    __coeff_a: np.ndarray
    __coeff_b: np.ndarray

    def __init__(
        self,
        N: int,
        fs: float,
        f_filter: list,
        use_iir_filter: bool,
        btype="low",
        ftype="butter",
        use_filtfilt=False,
    ):
        self.__sampling_rate = fs
        self.__coeffb_defined = False
        self.__coeffa_defined = False
        self.__use_filtfilt = use_filtfilt

        self.__filter_type_iir_used = use_iir_filter
        self.__filter_order = N
        self.__filter_corner = np.array(f_filter, dtype="float")
        self.__filt_ftype = self.__get_filter_ftype(ftype)
        self.__filt_btype = self.__get_filter_btype(btype)
        self.__extract_filter_params()

    def __extract_filter_params(self) -> None:
        if self.__filter_type_iir_used and not self.__filt_btype == "allpass":
            filter_params = scft.iirfilter(
                N=self.__filter_order,
                Wn=np.squeeze(2 * self.__filter_corner / self.__sampling_rate),
                btype=self.__filt_btype,
                ftype=self.__filt_ftype,
                analog=False,
                output="ba",
            )
            self.__coeff_b = filter_params[0]
            self.__coeffb_defined = True
            self.__coeff_a = np.array(filter_params[1])
            self.__coeffa_defined = True
        elif self.__filter_type_iir_used and self.__filt_btype == "allpass":
            match self.__filter_order:
                case 1:
                    val = np.tan(np.pi * self.__filter_corner[0] / self.__sampling_rate)
                    iir_c0 = (val - 1) / (val + 1)
                    self.__coeff_b = np.array([iir_c0, 1.0])
                    self.__coeffb_defined = True
                    self.__coeff_a = np.array([1.0, iir_c0])
                    self.__coeffa_defined = True
                case 2:
                    val = np.tan(np.pi * self.__filter_corner[1] / self.__sampling_rate)
                    iir_c0 = (val - 1) / (val + 1)
                    iir_c1 = -np.cos(2 * np.pi * self.__filter_corner[0] / self.__sampling_rate)
                    self.__coeff_b = np.array([-iir_c0, iir_c1 * (1 - iir_c0), 1.0])
                    self.__coeffb_defined = True
                    self.__coeff_a = np.array([1.0, iir_c1 * (1 - iir_c0), -iir_c0])
                    self.__coeffa_defined = True
                case _:
                    raise NotImplementedError(
                        "Allpass IIR-filters are only implemented for 1st and 2nd order! - Please change!"
                    )
        elif self.__filter_type_iir_used and self.__filt_btype == "allpass":
            raise NotImplementedError("Allpass Filter is only implemented for IIR filter types!")
        else:
            if self.__filt_btype == "allpass":
                self.__coeff_b = np.zeros(self.__filter_order + 1)
                self.__coeff_b[self.__filter_order] = 1.0
                self.__coeffb_defined = True
                self.__coeff_a = np.array(1.0)
                self.__coeffa_defined = False
            else:
                filter_params = scft.firwin(
                    numtaps=self.__filter_order,
                    cutoff=self.__filter_corner,
                    fs=self.__sampling_rate,
                    pass_zero=self.__filt_btype,
                )
                self.__coeff_b = filter_params
                self.__coeffb_defined = True
                self.__coeff_a = np.array(1.0)
                self.__coeffa_defined = False

    def __get_filter_btype(self, type_used: str) -> str:
        type_out = ""
        for key, type0 in self.__filt_btype_dict.items():
            if type_used == key:
                type_out = type0
                break
        if type_out == "":
            raise NotImplementedError("Type of used filter type is not available")
        return type_out

    def __get_filter_ftype(self, type_used: str) -> str:
        type_out = ""
        for key, type0 in self.__filt_ftype_dict.items():
            if type_used == key:
                type_out = type0
                break
        if type_out == "":
            raise NotImplementedError("Type of used filter type is not available")
        return type_out

    def filter(self, xin: np.ndarray) -> np.ndarray:
        return (
            scft.lfilter(b=self.__coeff_b, a=self.__coeff_a, x=xin)
            if not self.__use_filtfilt
            else scft.filtfilt(b=self.__coeff_b, a=self.__coeff_a, x=xin)
        )

    def freq_response(self, freq: np.ndarray) -> dict:
        if self.__filter_type_iir_used:
            fout = scft.iirfilter(
                N=self.__filter_order,
                Wn=np.squeeze(self.__filter_corner),
                btype=self.__filt_btype,
                ftype=self.__filt_ftype,
                analog=True,
                output="ba",
            )
            w, h = scft.freqs(b=fout[0], a=fout[1], worN=freq)
        else:
            w, h = scft.freqz(b=self.__coeff_b, a=1, fs=self.__sampling_rate, worN=freq)

        h0 = np.array(h)
        gain = np.abs(h0)
        phase = np.angle(h0, deg=True)
        return {"freq": w, "gain": gain, "phase": phase}
