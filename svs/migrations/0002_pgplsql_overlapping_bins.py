"""Create pg/plsql functions for creating list of overlapping UCSC bins."""
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("svs", "0001_initial")]

    operations = [
        migrations.RunSQL(
            r"""
                -- start and stop are 0-based positions
                CREATE OR REPLACE FUNCTION range_per_level(start integer, stop integer)
                    RETURNS TABLE(bin_start integer, bin_stop integer)
                AS
                $$
                DECLARE
                    bin_offsets constant integer[] := '{585,73,9,1,0}'::integer[];
                    shift_first constant integer := 17;
                    shift_next constant integer := 3;
                    max_position constant integer := 1 << 29;
                    max_bin constant integer := bin_offsets[0] + (max_position >> shift_first);

                    start_bin integer;
                    stop_bin integer;
                    bin_offset integer;
                BEGIN
                    IF start < 0 THEN
                        RAISE EXCEPTION 'Invalid start %s', start;
                    END IF;

                    start_bin = start >> shift_first;
                    stop_bin = stop >> shift_first;

                    FOREACH bin_offset IN ARRAY bin_offsets
                    LOOP
                        bin_start := bin_offset + start_bin;
                        bin_stop := bin_offset + stop_bin;
                        RAISE INFO 'return next = %, %', bin_start, bin_stop;
                        RETURN NEXT;
                        start_bin = start_bin >> shift_next;
                        stop_bin = stop_bin >> shift_next;
                    END LOOP;
                END
                $$
                LANGUAGE 'plpgsql'
                IMMUTABLE
                COST 1;

                -- start and stop are 0-based positions
                CREATE OR REPLACE FUNCTION overlapping_bins(start integer, stop integer)
                    RETURNS TABLE (bin integer)
                AS
                $$
                DECLARE
                    tmprow record;
                BEGIN
                    FOR tmprow IN
                        SELECT * FROM range_per_level(start, stop)
                    LOOP
                        RAISE INFO 'tmprow = %', tmprow;
                        RETURN QUERY
                            SELECT generate_series(tmprow.bin_start, tmprow.bin_stop);
                    END LOOP;
                END
                $$
                LANGUAGE 'plpgsql'
                IMMUTABLE
                COST 2;
            """,
            r"""
            DROP FUNCTION range_per_level(integer, integer);
            DROP FUNCTION overlapping_bins(integer, integer);
            """,
        )
    ]
