#!/usr/bin/env python
"""
Copyright (C) 2012 bendikro

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""
This program runs a sequence of commands on remote hosts using SSH.
"""
import itertools
import pprint
pp = pprint.PrettyPrinter(indent=4)

def main():
    import scheduler

    args = scheduler.parse_args()

    # Create session jobs from all variations of the following options:
    loss_values = ["0.5", "5", "fixedv 7,8,9,11,15,16,17,18,19,20,30 40"]
    options_values = ["", "-r"]
    payload_values = [100]
    itt_values = [100, 50]
    delay_values = [15, 50, 100]
    stream_count_values = [1]

    # We want session jobs that are structued something like this:
    """
    {'description': '1 thin rdb stream with fixed loss 1',
     'name_id': '1_thin_rdb_stream-fixed-loss_1',
     'substitutions': {'thin-rdb': {'loss': 'loss 1',
                                    'options': '-r',
                                    'stream': '-I i:30,S:20:5,d:20',
                                    'stream_count': '-c 1',
                                   }
                      },
     'timeout_secs': None
    }
    """
    session_job_list = []
    # Loop over the product of all the values in the value lists
    for loss, options, stream_count, itt, delay, payload in itertools.product(loss_values, options_values, stream_count_values, itt_values, delay_values, payload_values):
        sj = {}
        sj['substitutions'] = {}
        sj['substitutions']["thin-rdb"] = {}
        sj["substitutions"]["thin-rdb"]["loss"] = "loss %s" % loss
        sj["substitutions"]["thin-rdb"]["options"] = options
        sj["substitutions"]["thin-rdb"]["stream"] = "-I i:%d,S:%d" % (itt, payload)
        sj["substitutions"]["thin-rdb"]["stream_count"] = "-c %d" % stream_count

        stream_type = "rdb"
        if options == "":
            stream_type = ""
        loss_type = ""
        if loss.startswith("fixed"):
            loss_type = "fixed"
        else:
            loss_type = "%s" % loss

        sj["description"] = "%d thin %sstream with payload %d itt %d loss %s" % (stream_count, stream_type + "_" if stream_type else "", payload, itt, loss_type)
        sj["name_id"] =     "%d_thin_%sstream_payload_%d_itt_%d_loss_%s"  % (stream_count, stream_type + "_" if stream_type else "", payload, itt, loss_type)
        session_job_list.append(sj)

#    pp.pprint(session_job_list)

    settings, session_jobs, jobs, cleanup_jobs, scp_jobs = scheduler.setup(args, custom_session_jobs=session_job_list)
    scheduler.do_run_jobs(settings, session_jobs, jobs, cleanup_jobs, scp_jobs, args)

if __name__ == "__main__":
    main()
