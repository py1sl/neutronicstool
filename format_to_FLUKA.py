# FORMAT TO FLUKA
from math import log10, floor

import utilities as ut
import logging


# round down both flux and second values to 3 sf
def round_to_4sf(x):
    """ note: change value in front of int to change no. of sfs we round to
    """
    if x == 0:
        return 0
    else:
        return round(x, 4-int(floor(log10(abs(x))))-1)


# convert flux into scientific notation
def format_E(x):
    if x == 0:
        return '0.0'
    else:
        return'{:.2e}'.format(x)


def fluka_output():
    """ """
    df, maxlen = ut.read_excel('cyclemainoperationalparameters.xlsx')

    countdays = []
    countx = 0
    count0 = 0

    flux = []

    """ This loop extracts no. of days beam was on/off and flux amplitude from
        days it was on and appends it to the empty sets 'flux' and 'countdays'
    """
    for i in range(0, maxlen):
        if df[i] > 0 and (df[i]) == (df[i+1]):
            countx += 1
        elif df[i] > 0 and (df[i]) != (df[i+1]):
            countdays.append(countx)
            countx = 0
            flux.append(df[i])
        elif df[i] == 0 and (df[i]) == (df[i+1]):
            count0 += 1
        elif df[i] == 0 and (df[i]) != (df[i+1]):
            countdays.append(count0)
            count0 = 0
            flux.append(df[i])
        else:
            logging.debug('There is an error here!')

    # convert days into seconds
    countdays = [x * 24 * 60 * 60 for x in countdays]
    countdays = list(map(round_to_4sf, countdays))
    flux = list(map(round_to_4sf, flux))
    flux = list(map(format_E, flux))

    logging.debug(countdays)
    logging.debug(flux)

    logging.debug(type(flux[0]))
    logging.debug(type(flux[1]))

    tot = len(countdays)

    # write to FLUKA file

    file = open("fluka_test.i", "r+")
    # **** put something here to overwrite previous file ****
    # The conditionals are to satisfy FLUKAS input requirements.
    # These ensure beam flickers ON then OFF for corresponding values of flux

    for i in range(0, tot):  # could do step 3

        # write the comment lines
        if flux[i] == '0.0' and i % 3 == 2:  # end of line
            file.write("Beam OFF: "+str(countdays[i])+". seconds\n")
        elif flux[i] != '0.0' and i % 3 == 2:
            file.write("Beam ON: "+str(countdays[i])+". seconds\n")
        elif flux[i] == '0.0' and i % 3 == 0:  # beginning of line
            file.write("* Beam OFF: "+str(countdays[i])+". seconds,")
        elif flux[i] != '0.0' and i % 3 == 0:  # beginning of line
            file.write("* Beam ON: "+str(countdays[i])+". seconds,")
        elif flux[i] == '0.0':
            file.write("Beam OFF: "+str(countdays[i])+". seconds,")
        else:
            file.write("Beam ON: "+str(countdays[i])+". seconds,")

    file.close()

    # now write the IRRPROFI lines
    with open("fluka_test.i", "r+") as file:
        lines = file.readlines()
        numlines = len(lines)
        logging.debug("THIS IS NUMLINES= %i", numlines)

        x = -3
        for j in range(0, numlines):
            x = x + 3
            logging.debug("I'm x: %i", x)
            if tot % 3 == 1 and x == tot:  # end bit
                irrprofi = str("IRRPROFI"+(20 - (len(str(countdays[x]))+9))*" "
                           +str(countdays[x])+"."+(10-len(str(flux[x])))*" "
                           +str(flux[x]))
            elif tot % 3 == 2 and x == tot - 1:  # end bit
                 irrprofi = str("IRRPROFI"+(20 - (len(str(countdays[x]))+9))*" "
                           +str(countdays[x])+"."+(10-len(str(flux[x])))*" "
                           +str(flux[x])+(9-len(str(countdays[x+1])))*" "
                           +str(countdays[x+1])+"."+(10-len(str(flux[x+1])))*" "
                           +str(flux[x+1]))
            else:
                irrprofi = str("IRRPROFI"+(20 - (len(str(countdays[x]))+9))*" "
                           +str(countdays[x])+"."+(10-len(str(flux[x])))*" "
                           +str(flux[x])+(9-len(str(countdays[x+1])))*" "
                           +str(countdays[x+1])+"."+(10-len(str(flux[x+1])))*" "
                           +str(flux[x+1])+(9-len(str(countdays[x+2])))*" "
                           +str(countdays[x+2]) +"."+(10-len(str(flux[x+2])))*" "
                           +str(flux[x+2])+"\n")

            logging.debug("hi I'm j: %i", j)
            lines.insert(2*j+1, irrprofi)

        lines = "".join(lines)
        file.seek(0)
        file.write(lines)
        file.truncate()
    file.close()


if __name__ == "__main__":
    ut.setup_logging()
    fluka_output()
    logging.info("Completed irradiation history production")
