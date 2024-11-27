/**
 * MIT License
 *
 * Copyright (c) 2024 Pablo Rodriguez Nava, @pablintino
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 **/

create or replace view "KiCad Regulators DCDC" as
select distinct on (c.id) c.mpn                                  "Part Number",
                          c.value                                "Value",
                          c.manufacturer                         "Manufacturer",
                          c.created_on                           "Created On",
                          c.updated_on                           "Updated On",
                          c.package                              "Package",
                          c.description                          "Description",
                          c.comment_kicad                        "Comment",
                          c.operating_temperature_min            "Minimum Operating Temperature",
                          c.operating_temperature_max            "Maximum Operating Temperature",
                          CONCAT(l.alias, ':', l.reference)      "Symbol",
                          CONCAT_WS(';', ftp1, ftp2, ftp3, ftp4) "Footprints",
                          d.voltage_input_min                    "Minimum Input Voltage",
                          d.voltage_output_min_fixed             "Minimum/Fixed Output Voltage",
                          d.voltage_output_max                   "Maximum Output Voltage",
                          d.current_output                       "Output Current",
                          d.frequency_switching                  "Switching Frequency",
                          d.topology                             "Topology",
                          d.output_type                          "Output Type",
                          d.number_of_outputs                    "Number of Outputs"
from crosstab('select c.id, ROW_NUMBER() OVER (ORDER BY c.id, f.id) seq, CONCAT(f.alias, '':'', f.reference)
    from comp_voltage_regulator_dcdc d
             inner join component c
                        on d.id = c.id
             inner join component_footprint_asc cf
                        on c.id = cf.component_id
             inner join footprint_ref f
                        on cf.footprint_ref_id = f.id
             where f.cad_type = ''KICAD''::cadtype'
     ) as ct(cid int, ftp1 text, ftp2 text, ftp3 text, ftp4 text)
         right outer join component c on c.id = cid
         inner join comp_voltage_regulator_dcdc d on d.id = c.id
         inner join component_library_asc cl on cl.component_id = c.id
         left outer join library_ref l on cl.library_ref_id = l.id
where l.cad_type = 'KICAD'::cadtype
order by c.id desc;