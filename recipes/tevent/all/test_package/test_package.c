#include "tevent.h"

#include <stdio.h>
#include <unistd.h>
#include <sys/time.h>

struct state {
     struct timeval endtime;
     int counter;
     TALLOC_CTX *ctx;
};

static void callback(struct tevent_context *ev, struct tevent_timer *tim,
                     struct timeval current_time, void *private_data)
{
    struct state *data = talloc_get_type_abort(private_data, struct state);
    struct tevent_timer *time_event;
    struct timeval schedule;
    printf("Data value: %d\n", data->counter);
    fflush(stdout);
    data->counter += 1; // increase counter
    // if time has not reached its limit, set another event
    if (tevent_timeval_compare(&current_time, &(data->endtime)) < 0) {
        // do something
        // set repeat with delay 2 seconds
        schedule = tevent_timeval_current_ofs(0, 50000);
        time_event = tevent_add_timer(ev, data->ctx, schedule, callback, data);
        if (time_event == NULL) { // error ...
            fprintf(stderr, "MEMORY PROBLEM\n");
            return;
        }
    } else {
        // time limit exceeded
    }
}
int main(void)  {
    struct tevent_context *event_ctx;
    TALLOC_CTX *mem_ctx;
    struct tevent_timer *time_event;
    struct timeval schedule;

    mem_ctx = talloc_new(NULL); // parent
    event_ctx = tevent_context_init(mem_ctx);
    struct state *data = talloc(mem_ctx, struct state);
    schedule = tevent_timeval_current_ofs(0, 50000); // +50000 microseconds time value
    data->endtime = tevent_timeval_add(&schedule, 2, 0); // 2 seconds time limit
    data->ctx = mem_ctx;
    data->counter = 0;
    // add time event
    time_event = tevent_add_timer(event_ctx, mem_ctx, schedule, callback, data);
    if (time_event == NULL) {
        fprintf(stderr, "FAILED\n");
        return EXIT_FAILURE;
    }
    tevent_loop_wait(event_ctx);
    talloc_free(mem_ctx);
    return EXIT_SUCCESS;
}
