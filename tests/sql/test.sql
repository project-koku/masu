--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.5
-- Dumped by pg_dump version 10.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: testcustomer; Type: SCHEMA; Schema: -; Owner: kokuadmin
--

CREATE SCHEMA testcustomer;


ALTER SCHEMA testcustomer OWNER TO kokuadmin;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: api_customer; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.api_customer (
    group_ptr_id integer NOT NULL,
    date_created timestamp with time zone NOT NULL,
    owner_id integer,
    uuid uuid NOT NULL,
    schema_name text NOT NULL
);


ALTER TABLE public.api_customer OWNER TO kokuadmin;

--
-- Name: api_provider; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.api_provider (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    name character varying(256) NOT NULL,
    type character varying(50) NOT NULL,
    authentication_id integer,
    billing_source_id integer,
    created_by_id integer,
    customer_id integer,
    setup_complete boolean NOT NULL
);


ALTER TABLE public.api_provider OWNER TO kokuadmin;

--
-- Name: api_provider_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.api_provider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.api_provider_id_seq OWNER TO kokuadmin;

--
-- Name: api_provider_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.api_provider_id_seq OWNED BY public.api_provider.id;


--
-- Name: api_providerauthentication; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.api_providerauthentication (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    provider_resource_name text NOT NULL
);


ALTER TABLE public.api_providerauthentication OWNER TO kokuadmin;

--
-- Name: api_providerauthentication_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.api_providerauthentication_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.api_providerauthentication_id_seq OWNER TO kokuadmin;

--
-- Name: api_providerauthentication_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.api_providerauthentication_id_seq OWNED BY public.api_providerauthentication.id;


--
-- Name: api_providerbillingsource; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.api_providerbillingsource (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    bucket character varying(63) NOT NULL
);


ALTER TABLE public.api_providerbillingsource OWNER TO kokuadmin;

--
-- Name: api_providerbillingsource_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.api_providerbillingsource_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.api_providerbillingsource_id_seq OWNER TO kokuadmin;

--
-- Name: api_providerbillingsource_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.api_providerbillingsource_id_seq OWNED BY public.api_providerbillingsource.id;


--
-- Name: api_resettoken; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.api_resettoken (
    id integer NOT NULL,
    token uuid NOT NULL,
    expiration_date timestamp with time zone NOT NULL,
    used boolean NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.api_resettoken OWNER TO kokuadmin;

--
-- Name: api_resettoken_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.api_resettoken_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.api_resettoken_id_seq OWNER TO kokuadmin;

--
-- Name: api_resettoken_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.api_resettoken_id_seq OWNED BY public.api_resettoken.id;


--
-- Name: api_tenant; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.api_tenant (
    id integer NOT NULL,
    schema_name character varying(63) NOT NULL
);


ALTER TABLE public.api_tenant OWNER TO kokuadmin;

--
-- Name: api_tenant_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.api_tenant_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.api_tenant_id_seq OWNER TO kokuadmin;

--
-- Name: api_tenant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.api_tenant_id_seq OWNED BY public.api_tenant.id;


--
-- Name: api_user; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.api_user (
    user_ptr_id integer NOT NULL,
    uuid uuid NOT NULL
);


ALTER TABLE public.api_user OWNER TO kokuadmin;

--
-- Name: api_userpreference; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.api_userpreference (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    preference jsonb NOT NULL,
    user_id integer NOT NULL,
    description character varying(255),
    name character varying(255) NOT NULL
);


ALTER TABLE public.api_userpreference OWNER TO kokuadmin;

--
-- Name: api_userpreference_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.api_userpreference_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.api_userpreference_id_seq OWNER TO kokuadmin;

--
-- Name: api_userpreference_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.api_userpreference_id_seq OWNED BY public.api_userpreference.id;


--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO kokuadmin;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO kokuadmin;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO kokuadmin;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO kokuadmin;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO kokuadmin;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO kokuadmin;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO kokuadmin;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO kokuadmin;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_groups_id_seq OWNER TO kokuadmin;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.auth_user_groups_id_seq OWNED BY public.auth_user_groups.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_id_seq OWNER TO kokuadmin;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.auth_user_id_seq OWNED BY public.auth_user.id;


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO kokuadmin;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_user_permissions_id_seq OWNER TO kokuadmin;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.auth_user_user_permissions_id_seq OWNED BY public.auth_user_user_permissions.id;


--
-- Name: authtoken_token; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.authtoken_token (
    key character varying(40) NOT NULL,
    created timestamp with time zone NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.authtoken_token OWNER TO kokuadmin;

--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO kokuadmin;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO kokuadmin;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO kokuadmin;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO kokuadmin;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO kokuadmin;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO kokuadmin;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO kokuadmin;

--
-- Name: region_mapping; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.region_mapping (
    id integer NOT NULL,
    region character varying(32) NOT NULL,
    region_name character varying(64) NOT NULL
);


ALTER TABLE public.region_mapping OWNER TO kokuadmin;

--
-- Name: region_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.region_mapping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.region_mapping_id_seq OWNER TO kokuadmin;

--
-- Name: region_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.region_mapping_id_seq OWNED BY public.region_mapping.id;


--
-- Name: reporting_common_costusagereportstatus; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.reporting_common_costusagereportstatus (
    id integer NOT NULL,
    report_name character varying(128) NOT NULL,
    cursor_position integer NOT NULL,
    last_completed_datetime timestamp with time zone,
    last_started_datetime timestamp with time zone,
    etag character varying(64),
    provider_id integer,
    CONSTRAINT reporting_common_costusagereportstatus_cursor_position_check CHECK ((cursor_position >= 0))
);


ALTER TABLE public.reporting_common_costusagereportstatus OWNER TO kokuadmin;

--
-- Name: reporting_common_costusagereportstatus_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.reporting_common_costusagereportstatus_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reporting_common_costusagereportstatus_id_seq OWNER TO kokuadmin;

--
-- Name: reporting_common_costusagereportstatus_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.reporting_common_costusagereportstatus_id_seq OWNED BY public.reporting_common_costusagereportstatus.id;


--
-- Name: reporting_common_reportcolumnmap; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.reporting_common_reportcolumnmap (
    id integer NOT NULL,
    provider_type character varying(50) NOT NULL,
    provider_column_name character varying(128) NOT NULL,
    database_table character varying(50) NOT NULL,
    database_column character varying(128) NOT NULL
);


ALTER TABLE public.reporting_common_reportcolumnmap OWNER TO kokuadmin;

--
-- Name: reporting_common_reportcolumnmap_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.reporting_common_reportcolumnmap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reporting_common_reportcolumnmap_id_seq OWNER TO kokuadmin;

--
-- Name: reporting_common_reportcolumnmap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.reporting_common_reportcolumnmap_id_seq OWNED BY public.reporting_common_reportcolumnmap.id;


--
-- Name: si_unit_scale; Type: TABLE; Schema: public; Owner: kokuadmin
--

CREATE TABLE public.si_unit_scale (
    id integer NOT NULL,
    prefix character varying(12) NOT NULL,
    prefix_symbol character varying(1) NOT NULL,
    multiplying_factor numeric(49,24) NOT NULL
);


ALTER TABLE public.si_unit_scale OWNER TO kokuadmin;

--
-- Name: si_unit_scale_id_seq; Type: SEQUENCE; Schema: public; Owner: kokuadmin
--

CREATE SEQUENCE public.si_unit_scale_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.si_unit_scale_id_seq OWNER TO kokuadmin;

--
-- Name: si_unit_scale_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kokuadmin
--

ALTER SEQUENCE public.si_unit_scale_id_seq OWNED BY public.si_unit_scale.id;


--
-- Name: django_migrations; Type: TABLE; Schema: testcustomer; Owner: kokuadmin
--

CREATE TABLE testcustomer.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE testcustomer.django_migrations OWNER TO kokuadmin;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: testcustomer; Owner: kokuadmin
--

CREATE SEQUENCE testcustomer.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE testcustomer.django_migrations_id_seq OWNER TO kokuadmin;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: testcustomer; Owner: kokuadmin
--

ALTER SEQUENCE testcustomer.django_migrations_id_seq OWNED BY testcustomer.django_migrations.id;


--
-- Name: reporting_awsaccountalias; Type: TABLE; Schema: testcustomer; Owner: kokuadmin
--

CREATE TABLE testcustomer.reporting_awsaccountalias (
    id integer NOT NULL,
    account_id character varying(50) NOT NULL,
    account_alias character varying(63)
);


ALTER TABLE testcustomer.reporting_awsaccountalias OWNER TO kokuadmin;

--
-- Name: reporting_awsaccountalias_id_seq; Type: SEQUENCE; Schema: testcustomer; Owner: kokuadmin
--

CREATE SEQUENCE testcustomer.reporting_awsaccountalias_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE testcustomer.reporting_awsaccountalias_id_seq OWNER TO kokuadmin;

--
-- Name: reporting_awsaccountalias_id_seq; Type: SEQUENCE OWNED BY; Schema: testcustomer; Owner: kokuadmin
--

ALTER SEQUENCE testcustomer.reporting_awsaccountalias_id_seq OWNED BY testcustomer.reporting_awsaccountalias.id;


--
-- Name: reporting_awscostentry; Type: TABLE; Schema: testcustomer; Owner: kokuadmin
--

CREATE TABLE testcustomer.reporting_awscostentry (
    id integer NOT NULL,
    interval_start timestamp with time zone NOT NULL,
    interval_end timestamp with time zone NOT NULL,
    bill_id integer NOT NULL
);


ALTER TABLE testcustomer.reporting_awscostentry OWNER TO kokuadmin;

--
-- Name: reporting_awscostentry_id_seq; Type: SEQUENCE; Schema: testcustomer; Owner: kokuadmin
--

CREATE SEQUENCE testcustomer.reporting_awscostentry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE testcustomer.reporting_awscostentry_id_seq OWNER TO kokuadmin;

--
-- Name: reporting_awscostentry_id_seq; Type: SEQUENCE OWNED BY; Schema: testcustomer; Owner: kokuadmin
--

ALTER SEQUENCE testcustomer.reporting_awscostentry_id_seq OWNED BY testcustomer.reporting_awscostentry.id;


--
-- Name: reporting_awscostentrybill; Type: TABLE; Schema: testcustomer; Owner: kokuadmin
--

CREATE TABLE testcustomer.reporting_awscostentrybill (
    id integer NOT NULL,
    billing_resource character varying(50) NOT NULL,
    bill_type character varying(50) NOT NULL,
    payer_account_id character varying(50) NOT NULL,
    billing_period_start timestamp with time zone NOT NULL,
    billing_period_end timestamp with time zone NOT NULL
);


ALTER TABLE testcustomer.reporting_awscostentrybill OWNER TO kokuadmin;

--
-- Name: reporting_awscostentrybill_id_seq; Type: SEQUENCE; Schema: testcustomer; Owner: kokuadmin
--

CREATE SEQUENCE testcustomer.reporting_awscostentrybill_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE testcustomer.reporting_awscostentrybill_id_seq OWNER TO kokuadmin;

--
-- Name: reporting_awscostentrybill_id_seq; Type: SEQUENCE OWNED BY; Schema: testcustomer; Owner: kokuadmin
--

ALTER SEQUENCE testcustomer.reporting_awscostentrybill_id_seq OWNED BY testcustomer.reporting_awscostentrybill.id;


--
-- Name: reporting_awscostentrylineitem; Type: TABLE; Schema: testcustomer; Owner: kokuadmin
--

CREATE TABLE testcustomer.reporting_awscostentrylineitem (
    id bigint NOT NULL,
    tags jsonb,
    invoice_id character varying(63),
    line_item_type character varying(50) NOT NULL,
    usage_account_id character varying(50) NOT NULL,
    usage_start timestamp with time zone NOT NULL,
    usage_end timestamp with time zone NOT NULL,
    product_code character varying(50) NOT NULL,
    usage_type character varying(50),
    operation character varying(50),
    availability_zone character varying(50),
    resource_id character varying(256),
    usage_amount numeric(17,9),
    normalization_factor double precision,
    normalized_usage_amount numeric(17,9),
    currency_code character varying(10) NOT NULL,
    unblended_rate numeric(17,9),
    unblended_cost numeric(17,9),
    blended_rate numeric(17,9),
    blended_cost numeric(17,9),
    tax_type text,
    cost_entry_id integer NOT NULL,
    cost_entry_bill_id integer NOT NULL,
    cost_entry_pricing_id integer,
    cost_entry_product_id integer,
    cost_entry_reservation_id integer,
    hash text,
    public_on_demand_cost numeric(17,9),
    public_on_demand_rate numeric(17,9),
    reservation_amortized_upfront_cost_for_usage numeric(17,9),
    reservation_amortized_upfront_fee numeric(17,9),
    reservation_recurring_fee_for_usage numeric(17,9),
    reservation_unused_quantity numeric(17,9),
    reservation_unused_recurring_fee numeric(17,9)
);


ALTER TABLE testcustomer.reporting_awscostentrylineitem OWNER TO kokuadmin;

--
-- Name: reporting_awscostentrylineitem_aggregates; Type: TABLE; Schema: testcustomer; Owner: kokuadmin
--

CREATE TABLE testcustomer.reporting_awscostentrylineitem_aggregates (
    id integer NOT NULL,
    time_scope_value integer NOT NULL,
    report_type character varying(50) NOT NULL,
    usage_account_id character varying(50),
    product_code character varying(50) NOT NULL,
    region character varying(50),
    availability_zone character varying(50),
    usage_amount numeric(17,9),
    unblended_cost numeric(17,9),
    resource_count integer
);


ALTER TABLE testcustomer.reporting_awscostentrylineitem_aggregates OWNER TO kokuadmin;

--
-- Name: reporting_awscostentrylineitem_aggregates_id_seq; Type: SEQUENCE; Schema: testcustomer; Owner: kokuadmin
--

CREATE SEQUENCE testcustomer.reporting_awscostentrylineitem_aggregates_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE testcustomer.reporting_awscostentrylineitem_aggregates_id_seq OWNER TO kokuadmin;

--
-- Name: reporting_awscostentrylineitem_aggregates_id_seq; Type: SEQUENCE OWNED BY; Schema: testcustomer; Owner: kokuadmin
--

ALTER SEQUENCE testcustomer.reporting_awscostentrylineitem_aggregates_id_seq OWNED BY testcustomer.reporting_awscostentrylineitem_aggregates.id;


--
-- Name: reporting_awscostentrylineitem_daily; Type: TABLE; Schema: testcustomer; Owner: kokuadmin
--

CREATE TABLE testcustomer.reporting_awscostentrylineitem_daily (
    id bigint NOT NULL,
    line_item_type character varying(50) NOT NULL,
    usage_account_id character varying(50) NOT NULL,
    usage_start date NOT NULL,
    product_code character varying(50) NOT NULL,
    usage_type character varying(50),
    operation character varying(50),
    availability_zone character varying(50),
    resource_id character varying(256),
    usage_amount double precision,
    normalization_factor double precision,
    normalized_usage_amount double precision,
    currency_code character varying(10) NOT NULL,
    unblended_rate numeric(17,9),
    unblended_cost numeric(17,9),
    blended_rate numeric(17,9),
    blended_cost numeric(17,9),
    public_on_demand_cost numeric(17,9),
    public_on_demand_rate numeric(17,9),
    tax_type text,
    tags jsonb,
    cost_entry_pricing_id integer,
    cost_entry_product_id integer,
    cost_entry_reservation_id integer
);


ALTER TABLE testcustomer.reporting_awscostentrylineitem_daily OWNER TO kokuadmin;

--
-- Name: reporting_awscostentrylineitem_daily_id_seq; Type: SEQUENCE; Schema: testcustomer; Owner: kokuadmin
--

CREATE SEQUENCE testcustomer.reporting_awscostentrylineitem_daily_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE testcustomer.reporting_awscostentrylineitem_daily_id_seq OWNER TO kokuadmin;

--
-- Name: reporting_awscostentrylineitem_daily_id_seq; Type: SEQUENCE OWNED BY; Schema: testcustomer; Owner: kokuadmin
--

ALTER SEQUENCE testcustomer.reporting_awscostentrylineitem_daily_id_seq OWNED BY testcustomer.reporting_awscostentrylineitem_daily.id;


--
-- Name: reporting_awscostentrylineitem_daily_summary; Type: TABLE; Schema: testcustomer; Owner: kokuadmin
--

CREATE TABLE testcustomer.reporting_awscostentrylineitem_daily_summary (
    id bigint NOT NULL,
    usage_start date NOT NULL,
    usage_account_id character varying(50) NOT NULL,
    product_code character varying(50) NOT NULL,
    product_family character varying(150),
    availability_zone character varying(50),
    region character varying(50),
    instance_type character varying(50),
    unit character varying(63),
    resource_count integer,
    usage_amount double precision,
    normalization_factor double precision,
    normalized_usage_amount double precision,
    currency_code character varying(10) NOT NULL,
    unblended_rate numeric(17,9),
    unblended_cost numeric(17,9),
    blended_rate numeric(17,9),
    blended_cost numeric(17,9),
    public_on_demand_cost numeric(17,9),
    public_on_demand_rate numeric(17,9),
    tax_type text
);


ALTER TABLE testcustomer.reporting_awscostentrylineitem_daily_summary OWNER TO kokuadmin;

--
-- Name: reporting_awscostentrylineitem_daily_summary_id_seq; Type: SEQUENCE; Schema: testcustomer; Owner: kokuadmin
--

CREATE SEQUENCE testcustomer.reporting_awscostentrylineitem_daily_summary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE testcustomer.reporting_awscostentrylineitem_daily_summary_id_seq OWNER TO kokuadmin;

--
-- Name: reporting_awscostentrylineitem_daily_summary_id_seq; Type: SEQUENCE OWNED BY; Schema: testcustomer; Owner: kokuadmin
--

ALTER SEQUENCE testcustomer.reporting_awscostentrylineitem_daily_summary_id_seq OWNED BY testcustomer.reporting_awscostentrylineitem_daily_summary.id;


--
-- Name: reporting_awscostentrylineitem_id_seq; Type: SEQUENCE; Schema: testcustomer; Owner: kokuadmin
--

CREATE SEQUENCE testcustomer.reporting_awscostentrylineitem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE testcustomer.reporting_awscostentrylineitem_id_seq OWNER TO kokuadmin;

--
-- Name: reporting_awscostentrylineitem_id_seq; Type: SEQUENCE OWNED BY; Schema: testcustomer; Owner: kokuadmin
--

ALTER SEQUENCE testcustomer.reporting_awscostentrylineitem_id_seq OWNED BY testcustomer.reporting_awscostentrylineitem.id;


--
-- Name: reporting_awscostentrypricing; Type: TABLE; Schema: testcustomer; Owner: kokuadmin
--

CREATE TABLE testcustomer.reporting_awscostentrypricing (
    id integer NOT NULL,
    term character varying(63),
    unit character varying(63)
);


ALTER TABLE testcustomer.reporting_awscostentrypricing OWNER TO kokuadmin;

--
-- Name: reporting_awscostentrypricing_id_seq; Type: SEQUENCE; Schema: testcustomer; Owner: kokuadmin
--

CREATE SEQUENCE testcustomer.reporting_awscostentrypricing_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE testcustomer.reporting_awscostentrypricing_id_seq OWNER TO kokuadmin;

--
-- Name: reporting_awscostentrypricing_id_seq; Type: SEQUENCE OWNED BY; Schema: testcustomer; Owner: kokuadmin
--

ALTER SEQUENCE testcustomer.reporting_awscostentrypricing_id_seq OWNED BY testcustomer.reporting_awscostentrypricing.id;


--
-- Name: reporting_awscostentryproduct; Type: TABLE; Schema: testcustomer; Owner: kokuadmin
--

CREATE TABLE testcustomer.reporting_awscostentryproduct (
    id integer NOT NULL,
    sku character varying(128),
    product_name character varying(63),
    product_family character varying(150),
    service_code character varying(50),
    region character varying(50),
    instance_type character varying(50),
    memory double precision,
    vcpu integer,
    memory_unit character varying(24),
    CONSTRAINT reporting_awscostentryproduct_vcpu_check CHECK ((vcpu >= 0))
);


ALTER TABLE testcustomer.reporting_awscostentryproduct OWNER TO kokuadmin;

--
-- Name: reporting_awscostentryproduct_id_seq; Type: SEQUENCE; Schema: testcustomer; Owner: kokuadmin
--

CREATE SEQUENCE testcustomer.reporting_awscostentryproduct_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE testcustomer.reporting_awscostentryproduct_id_seq OWNER TO kokuadmin;

--
-- Name: reporting_awscostentryproduct_id_seq; Type: SEQUENCE OWNED BY; Schema: testcustomer; Owner: kokuadmin
--

ALTER SEQUENCE testcustomer.reporting_awscostentryproduct_id_seq OWNED BY testcustomer.reporting_awscostentryproduct.id;


--
-- Name: reporting_awscostentryreservation; Type: TABLE; Schema: testcustomer; Owner: kokuadmin
--

CREATE TABLE testcustomer.reporting_awscostentryreservation (
    id integer NOT NULL,
    reservation_arn text NOT NULL,
    number_of_reservations integer,
    units_per_reservation numeric(17,9),
    start_time timestamp with time zone,
    end_time timestamp with time zone,
    CONSTRAINT reporting_awscostentryreservation_number_of_reservations_check CHECK ((number_of_reservations >= 0))
);


ALTER TABLE testcustomer.reporting_awscostentryreservation OWNER TO kokuadmin;

--
-- Name: reporting_awscostentryreservation_id_seq; Type: SEQUENCE; Schema: testcustomer; Owner: kokuadmin
--

CREATE SEQUENCE testcustomer.reporting_awscostentryreservation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE testcustomer.reporting_awscostentryreservation_id_seq OWNER TO kokuadmin;

--
-- Name: reporting_awscostentryreservation_id_seq; Type: SEQUENCE OWNED BY; Schema: testcustomer; Owner: kokuadmin
--

ALTER SEQUENCE testcustomer.reporting_awscostentryreservation_id_seq OWNED BY testcustomer.reporting_awscostentryreservation.id;


--
-- Name: api_provider id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_provider ALTER COLUMN id SET DEFAULT nextval('public.api_provider_id_seq'::regclass);


--
-- Name: api_providerauthentication id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_providerauthentication ALTER COLUMN id SET DEFAULT nextval('public.api_providerauthentication_id_seq'::regclass);


--
-- Name: api_providerbillingsource id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_providerbillingsource ALTER COLUMN id SET DEFAULT nextval('public.api_providerbillingsource_id_seq'::regclass);


--
-- Name: api_resettoken id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_resettoken ALTER COLUMN id SET DEFAULT nextval('public.api_resettoken_id_seq'::regclass);


--
-- Name: api_tenant id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_tenant ALTER COLUMN id SET DEFAULT nextval('public.api_tenant_id_seq'::regclass);


--
-- Name: api_userpreference id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_userpreference ALTER COLUMN id SET DEFAULT nextval('public.api_userpreference_id_seq'::regclass);


--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);


--
-- Name: auth_user id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_user ALTER COLUMN id SET DEFAULT nextval('public.auth_user_id_seq'::regclass);


--
-- Name: auth_user_groups id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_user_groups ALTER COLUMN id SET DEFAULT nextval('public.auth_user_groups_id_seq'::regclass);


--
-- Name: auth_user_user_permissions id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_user_user_permissions_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Name: region_mapping id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.region_mapping ALTER COLUMN id SET DEFAULT nextval('public.region_mapping_id_seq'::regclass);


--
-- Name: reporting_common_costusagereportstatus id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.reporting_common_costusagereportstatus ALTER COLUMN id SET DEFAULT nextval('public.reporting_common_costusagereportstatus_id_seq'::regclass);


--
-- Name: reporting_common_reportcolumnmap id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.reporting_common_reportcolumnmap ALTER COLUMN id SET DEFAULT nextval('public.reporting_common_reportcolumnmap_id_seq'::regclass);


--
-- Name: si_unit_scale id; Type: DEFAULT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.si_unit_scale ALTER COLUMN id SET DEFAULT nextval('public.si_unit_scale_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.django_migrations ALTER COLUMN id SET DEFAULT nextval('testcustomer.django_migrations_id_seq'::regclass);


--
-- Name: reporting_awsaccountalias id; Type: DEFAULT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awsaccountalias ALTER COLUMN id SET DEFAULT nextval('testcustomer.reporting_awsaccountalias_id_seq'::regclass);


--
-- Name: reporting_awscostentry id; Type: DEFAULT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentry ALTER COLUMN id SET DEFAULT nextval('testcustomer.reporting_awscostentry_id_seq'::regclass);


--
-- Name: reporting_awscostentrybill id; Type: DEFAULT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrybill ALTER COLUMN id SET DEFAULT nextval('testcustomer.reporting_awscostentrybill_id_seq'::regclass);


--
-- Name: reporting_awscostentrylineitem id; Type: DEFAULT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem ALTER COLUMN id SET DEFAULT nextval('testcustomer.reporting_awscostentrylineitem_id_seq'::regclass);


--
-- Name: reporting_awscostentrylineitem_aggregates id; Type: DEFAULT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem_aggregates ALTER COLUMN id SET DEFAULT nextval('testcustomer.reporting_awscostentrylineitem_aggregates_id_seq'::regclass);


--
-- Name: reporting_awscostentrylineitem_daily id; Type: DEFAULT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem_daily ALTER COLUMN id SET DEFAULT nextval('testcustomer.reporting_awscostentrylineitem_daily_id_seq'::regclass);


--
-- Name: reporting_awscostentrylineitem_daily_summary id; Type: DEFAULT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem_daily_summary ALTER COLUMN id SET DEFAULT nextval('testcustomer.reporting_awscostentrylineitem_daily_summary_id_seq'::regclass);


--
-- Name: reporting_awscostentrypricing id; Type: DEFAULT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrypricing ALTER COLUMN id SET DEFAULT nextval('testcustomer.reporting_awscostentrypricing_id_seq'::regclass);


--
-- Name: reporting_awscostentryproduct id; Type: DEFAULT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentryproduct ALTER COLUMN id SET DEFAULT nextval('testcustomer.reporting_awscostentryproduct_id_seq'::regclass);


--
-- Name: reporting_awscostentryreservation id; Type: DEFAULT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentryreservation ALTER COLUMN id SET DEFAULT nextval('testcustomer.reporting_awscostentryreservation_id_seq'::regclass);


--
-- Data for Name: api_customer; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.api_customer (group_ptr_id, date_created, owner_id, uuid, schema_name) FROM stdin;
1	2018-09-18 17:36:29.612193+00	2	2b498175-4258-4bc1-9c6d-62ce0960345c	testcustomer
\.


--
-- Data for Name: api_provider; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.api_provider (id, uuid, name, type, authentication_id, billing_source_id, created_by_id, customer_id, setup_complete) FROM stdin;
1	6e212746-484a-40cd-bba0-09a19d132d64	Test Provider	AWS	1	1	2	1	f
\.


--
-- Data for Name: api_providerauthentication; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.api_providerauthentication (id, uuid, provider_resource_name) FROM stdin;
1	7e4ec31b-7ced-4a17-9f7e-f77e9efa8fd6	arn:aws:iam::111111111111:role/CostManagement
\.


--
-- Data for Name: api_providerbillingsource; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.api_providerbillingsource (id, uuid, bucket) FROM stdin;
1	75b17096-319a-45ec-92c1-18dbd5e78f94	test-bucket
\.


--
-- Data for Name: api_resettoken; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.api_resettoken (id, token, expiration_date, used, user_id) FROM stdin;
1	c461920a-91e2-44a5-9394-b1a8bbade5df	2018-09-19 17:36:29.603072+00	f	2
\.


--
-- Data for Name: api_tenant; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.api_tenant (id, schema_name) FROM stdin;
1	public
2	testcustomer
\.


--
-- Data for Name: api_user; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.api_user (user_ptr_id, uuid) FROM stdin;
1	a0dc7eca-026a-43a6-a41b-d68d8517f62e
2	87c64760-6897-4bcf-9657-171da3c2c6f3
\.


--
-- Data for Name: api_userpreference; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.api_userpreference (id, uuid, preference, user_id, description, name) FROM stdin;
1	4e73f8a1-37b3-4713-ab9d-d29608d47ed9	{"currency": "USD"}	2	default preference	currency
2	a826b56f-f712-47ad-8d7a-6cc606b8ff3b	{"timezone": "UTC"}	2	default preference	timezone
3	d041cc4e-407d-4e4a-8340-6b001b8a146f	{"locale": "en_US.UTF-8"}	2	default preference	locale
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.auth_group (id, name) FROM stdin;
1	Test Customer
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add user	4	add_user
14	Can change user	4	change_user
15	Can delete user	4	delete_user
16	Can view user	4	view_user
17	Can add content type	5	add_contenttype
18	Can change content type	5	change_contenttype
19	Can delete content type	5	delete_contenttype
20	Can view content type	5	view_contenttype
21	Can add session	6	add_session
22	Can change session	6	change_session
23	Can delete session	6	delete_session
24	Can view session	6	view_session
25	Can add Token	7	add_token
26	Can change Token	7	change_token
27	Can delete Token	7	delete_token
28	Can view Token	7	view_token
29	Can add customer	8	add_customer
30	Can change customer	8	change_customer
31	Can delete customer	8	delete_customer
32	Can view customer	8	view_customer
33	Can add user	9	add_user
34	Can change user	9	change_user
35	Can delete user	9	delete_user
36	Can view user	9	view_user
37	Can add reset token	10	add_resettoken
38	Can change reset token	10	change_resettoken
39	Can delete reset token	10	delete_resettoken
40	Can view reset token	10	view_resettoken
41	Can add user preference	11	add_userpreference
42	Can change user preference	11	change_userpreference
43	Can delete user preference	11	delete_userpreference
44	Can view user preference	11	view_userpreference
45	Can add provider	12	add_provider
46	Can change provider	12	change_provider
47	Can delete provider	12	delete_provider
48	Can view provider	12	view_provider
49	Can add provider authentication	13	add_providerauthentication
50	Can change provider authentication	13	change_providerauthentication
51	Can delete provider authentication	13	delete_providerauthentication
52	Can view provider authentication	13	view_providerauthentication
53	Can add provider billing source	14	add_providerbillingsource
54	Can change provider billing source	14	change_providerbillingsource
55	Can delete provider billing source	14	delete_providerbillingsource
56	Can view provider billing source	14	view_providerbillingsource
57	Can add tenant	15	add_tenant
58	Can change tenant	15	change_tenant
59	Can delete tenant	15	delete_tenant
60	Can view tenant	15	view_tenant
61	Can add aws cost entry	16	add_awscostentry
62	Can change aws cost entry	16	change_awscostentry
63	Can delete aws cost entry	16	delete_awscostentry
64	Can view aws cost entry	16	view_awscostentry
65	Can add aws cost entry bill	17	add_awscostentrybill
66	Can change aws cost entry bill	17	change_awscostentrybill
67	Can delete aws cost entry bill	17	delete_awscostentrybill
68	Can view aws cost entry bill	17	view_awscostentrybill
69	Can add aws cost entry line item	18	add_awscostentrylineitem
70	Can change aws cost entry line item	18	change_awscostentrylineitem
71	Can delete aws cost entry line item	18	delete_awscostentrylineitem
72	Can view aws cost entry line item	18	view_awscostentrylineitem
73	Can add aws cost entry pricing	19	add_awscostentrypricing
74	Can change aws cost entry pricing	19	change_awscostentrypricing
75	Can delete aws cost entry pricing	19	delete_awscostentrypricing
76	Can view aws cost entry pricing	19	view_awscostentrypricing
77	Can add aws cost entry product	20	add_awscostentryproduct
78	Can change aws cost entry product	20	change_awscostentryproduct
79	Can delete aws cost entry product	20	delete_awscostentryproduct
80	Can view aws cost entry product	20	view_awscostentryproduct
81	Can add aws cost entry reservation	21	add_awscostentryreservation
82	Can change aws cost entry reservation	21	change_awscostentryreservation
83	Can delete aws cost entry reservation	21	delete_awscostentryreservation
84	Can view aws cost entry reservation	21	view_awscostentryreservation
85	Can add aws cost entry line item aggregates	22	add_awscostentrylineitemaggregates
86	Can change aws cost entry line item aggregates	22	change_awscostentrylineitemaggregates
87	Can delete aws cost entry line item aggregates	22	delete_awscostentrylineitemaggregates
88	Can view aws cost entry line item aggregates	22	view_awscostentrylineitemaggregates
89	Can add aws cost entry line item daily	23	add_awscostentrylineitemdaily
90	Can change aws cost entry line item daily	23	change_awscostentrylineitemdaily
91	Can delete aws cost entry line item daily	23	delete_awscostentrylineitemdaily
92	Can view aws cost entry line item daily	23	view_awscostentrylineitemdaily
93	Can add aws cost entry line item daily summary	24	add_awscostentrylineitemdailysummary
94	Can change aws cost entry line item daily summary	24	change_awscostentrylineitemdailysummary
95	Can delete aws cost entry line item daily summary	24	delete_awscostentrylineitemdailysummary
96	Can view aws cost entry line item daily summary	24	view_awscostentrylineitemdailysummary
97	Can add aws account alias	25	add_awsaccountalias
98	Can change aws account alias	25	change_awsaccountalias
99	Can delete aws account alias	25	delete_awsaccountalias
100	Can view aws account alias	25	view_awsaccountalias
101	Can add report column map	26	add_reportcolumnmap
102	Can change report column map	26	change_reportcolumnmap
103	Can delete report column map	26	delete_reportcolumnmap
104	Can view report column map	26	view_reportcolumnmap
105	Can add cost usage report status	27	add_costusagereportstatus
106	Can change cost usage report status	27	change_costusagereportstatus
107	Can delete cost usage report status	27	delete_costusagereportstatus
108	Can view cost usage report status	27	view_costusagereportstatus
109	Can add si unit scale	28	add_siunitscale
110	Can change si unit scale	28	change_siunitscale
111	Can delete si unit scale	28	delete_siunitscale
112	Can view si unit scale	28	view_siunitscale
113	Can add region mapping	29	add_regionmapping
114	Can change region mapping	29	change_regionmapping
115	Can delete region mapping	29	delete_regionmapping
116	Can view region mapping	29	view_regionmapping
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
1	pbkdf2_sha256$120000$jf6yOEd8KULl$5eCxupWGGF8mhN+aplUX1V/L55bjh8ADdgsYQ2Txkz8=	\N	t	admin			admin@example.com	t	t	2018-09-18 17:36:19.641122+00
2	pbkdf2_sha256$120000$W0IpbsawR2z2$2CdYqxKGpytq8k5OB7HHGvsE/XTyDCiQa8EbC7N1S58=	\N	f	test_customer			test@example.com	f	t	2018-09-18 17:36:29.359585+00
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
1	2	1
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: authtoken_token; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.authtoken_token (key, created, user_id) FROM stdin;
0f070d5acffabfc4d4e79302f1531f96c3ac4449	2018-09-18 17:36:29.266173+00	1
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	authtoken	token
8	api	customer
9	api	user
10	api	resettoken
11	api	userpreference
12	api	provider
13	api	providerauthentication
14	api	providerbillingsource
15	api	tenant
16	reporting	awscostentry
17	reporting	awscostentrybill
18	reporting	awscostentrylineitem
19	reporting	awscostentrypricing
20	reporting	awscostentryproduct
21	reporting	awscostentryreservation
22	reporting	awscostentrylineitemaggregates
23	reporting	awscostentrylineitemdaily
24	reporting	awscostentrylineitemdailysummary
25	reporting	awsaccountalias
26	reporting_common	reportcolumnmap
27	reporting_common	costusagereportstatus
28	reporting_common	siunitscale
29	reporting_common	regionmapping
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2018-09-18 17:36:18.452898+00
2	auth	0001_initial	2018-09-18 17:36:18.603537+00
3	admin	0001_initial	2018-09-18 17:36:18.647259+00
4	admin	0002_logentry_remove_auto_add	2018-09-18 17:36:18.66265+00
5	admin	0003_logentry_add_action_flag_choices	2018-09-18 17:36:18.679424+00
6	contenttypes	0002_remove_content_type_name	2018-09-18 17:36:18.710716+00
7	auth	0002_alter_permission_name_max_length	2018-09-18 17:36:18.728587+00
8	auth	0003_alter_user_email_max_length	2018-09-18 17:36:18.751882+00
9	auth	0004_alter_user_username_opts	2018-09-18 17:36:18.765918+00
10	auth	0005_alter_user_last_login_null	2018-09-18 17:36:18.787715+00
11	auth	0006_require_contenttypes_0002	2018-09-18 17:36:18.796588+00
12	auth	0007_alter_validators_add_error_messages	2018-09-18 17:36:18.811203+00
13	auth	0008_alter_user_username_max_length	2018-09-18 17:36:18.838653+00
14	auth	0009_alter_user_last_name_max_length	2018-09-18 17:36:18.860489+00
15	api	0001_initial	2018-09-18 17:36:18.877597+00
16	api	0002_auto_20180509_1400	2018-09-18 17:36:18.937223+00
17	api	0003_auto_20180509_1849	2018-09-18 17:36:19.011119+00
18	api	0004_auto_20180510_1824	2018-09-18 17:36:19.11117+00
19	api	0005_auto_20180511_1445	2018-09-18 17:36:19.148897+00
20	api	0006_resettoken	2018-09-18 17:36:19.200098+00
21	api	0007_userpreference	2018-09-18 17:36:19.243876+00
22	api	0008_provider	2018-09-18 17:36:19.36719+00
23	api	0009_auto_20180523_0045	2018-09-18 17:36:19.40594+00
24	api	0010_auto_20180523_1540	2018-09-18 17:36:19.462471+00
25	api	0011_auto_20180524_1838	2018-09-18 17:36:19.515913+00
26	api	0012_auto_20180529_1526	2018-09-18 17:36:19.677889+00
27	api	0013_auto_20180531_1921	2018-09-18 17:36:19.700682+00
28	api	0014_costusagereportstatus	2018-09-18 17:36:19.741582+00
29	api	0015_auto_20180614_1343	2018-09-18 17:36:19.782324+00
30	api	0016_auto_20180802_1911	2018-09-18 17:36:19.802346+00
31	api	0017_auto_20180815_1716	2018-09-18 17:36:19.829861+00
32	api	0018_delete_status	2018-09-18 17:36:19.844241+00
33	api	0019_provider_setup_complete	2018-09-18 17:36:19.87916+00
34	authtoken	0001_initial	2018-09-18 17:36:19.915282+00
35	authtoken	0002_auto_20160226_1747	2018-09-18 17:36:19.972064+00
36	reporting	0001_initial	2018-09-18 17:36:20.027579+00
37	reporting	0002_auto_20180615_1725	2018-09-18 17:36:20.263584+00
38	reporting	0003_auto_20180619_1833	2018-09-18 17:36:20.344322+00
39	reporting	0004_auto_20180803_1926	2018-09-18 17:36:20.373126+00
40	reporting	0005_auto_20180807_1819	2018-09-18 17:36:20.413669+00
41	reporting	0006_auto_20180821_1654	2018-09-18 17:36:20.5111+00
42	reporting	0007_auto_20180824_0035	2018-09-18 17:36:20.592489+00
43	reporting	0008_awsaccountalias	2018-09-18 17:36:20.606429+00
44	reporting_common	0001_initial	2018-09-18 17:36:20.634508+00
45	reporting_common	0002_auto_20180608_1647	2018-09-18 17:36:20.775834+00
46	reporting_common	0003_costusagereportstatus	2018-09-18 17:36:20.819816+00
47	reporting_common	0004_siunitscale	2018-09-18 17:36:20.874886+00
48	reporting_common	0005_auto_20180725_1523	2018-09-18 17:36:21.052599+00
49	reporting_common	0006_auto_20180802_1911	2018-09-18 17:36:21.070691+00
50	reporting_common	0007_auto_20180808_2134	2018-09-18 17:36:21.112372+00
51	sessions	0001_initial	2018-09-18 17:36:21.170247+00
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Data for Name: region_mapping; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.region_mapping (id, region, region_name) FROM stdin;
\.


--
-- Data for Name: reporting_common_costusagereportstatus; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.reporting_common_costusagereportstatus (id, report_name, cursor_position, last_completed_datetime, last_started_datetime, etag, provider_id) FROM stdin;
\.


--
-- Data for Name: reporting_common_reportcolumnmap; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.reporting_common_reportcolumnmap (id, provider_type, provider_column_name, database_table, database_column) FROM stdin;
1	AWS	bill/BillingEntity	reporting_awscostentrybill	billing_resource
2	AWS	bill/BillType	reporting_awscostentrybill	bill_type
3	AWS	bill/PayerAccountId	reporting_awscostentrybill	payer_account_id
4	AWS	bill/BillingPeriodStartDate	reporting_awscostentrybill	billing_period_start
5	AWS	bill/BillingPeriodEndDate	reporting_awscostentrybill	billing_period_end
6	AWS	bill/InvoiceId	reporting_awscostentrylineitem	invoice_id
7	AWS	lineItem/LineItemType	reporting_awscostentrylineitem	line_item_type
8	AWS	lineItem/UsageAccountId	reporting_awscostentrylineitem	usage_account_id
9	AWS	lineItem/UsageStartDate	reporting_awscostentrylineitem	usage_start
10	AWS	lineItem/UsageEndDate	reporting_awscostentrylineitem	usage_end
11	AWS	lineItem/ProductCode	reporting_awscostentrylineitem	product_code
12	AWS	lineItem/UsageType	reporting_awscostentrylineitem	usage_type
13	AWS	lineItem/Operation	reporting_awscostentrylineitem	operation
14	AWS	lineItem/AvailabilityZone	reporting_awscostentrylineitem	availability_zone
15	AWS	lineItem/ResourceId	reporting_awscostentrylineitem	resource_id
16	AWS	lineItem/UsageAmount	reporting_awscostentrylineitem	usage_amount
17	AWS	lineItem/NormalizationFactor	reporting_awscostentrylineitem	normalization_factor
18	AWS	lineItem/NormalizedUsageAmount	reporting_awscostentrylineitem	normalized_usage_amount
19	AWS	lineItem/CurrencyCode	reporting_awscostentrylineitem	currency_code
20	AWS	lineItem/UnblendedRate	reporting_awscostentrylineitem	unblended_rate
21	AWS	lineItem/UnblendedCost	reporting_awscostentrylineitem	unblended_cost
22	AWS	lineItem/BlendedRate	reporting_awscostentrylineitem	blended_rate
23	AWS	lineItem/BlendedCost	reporting_awscostentrylineitem	blended_cost
24	AWS	lineItem/TaxType	reporting_awscostentrylineitem	tax_type
25	AWS	pricing/publicOnDemandCost	reporting_awscostentrylineitem	public_on_demand_cost
26	AWS	pricing/publicOnDemandRate	reporting_awscostentrylineitem	public_on_demand_rate
27	AWS	pricing/term	reporting_awscostentrypricing	term
28	AWS	pricing/unit	reporting_awscostentrypricing	unit
29	AWS	product/sku	reporting_awscostentryproduct	sku
30	AWS	product/ProductName	reporting_awscostentryproduct	product_name
31	AWS	product/productFamily	reporting_awscostentryproduct	product_family
32	AWS	product/servicecode	reporting_awscostentryproduct	service_code
33	AWS	product/region	reporting_awscostentryproduct	region
34	AWS	product/instanceType	reporting_awscostentryproduct	instance_type
35	AWS	product/memory	reporting_awscostentryproduct	memory
36	AWS	product/memory_unit	reporting_awscostentryproduct	memory_unit
37	AWS	product/vcpu	reporting_awscostentryproduct	vcpu
38	AWS	reservation/ReservationARN	reporting_awscostentryreservation	reservation_arn
39	AWS	reservation/NumberOfReservations	reporting_awscostentryreservation	number_of_reservations
40	AWS	reservation/UnitsPerReservation	reporting_awscostentryreservation	units_per_reservation
41	AWS	reservation/StartTime	reporting_awscostentryreservation	start_time
42	AWS	reservation/EndTime	reporting_awscostentryreservation	end_time
43	AWS	reservation/AmortizedUpfrontFeeForBillingPeriod	reporting_awscostentrylineitem	reservation_amortized_upfront_fee
44	AWS	reservation/AmortizedUpfrontCostForUsage	reporting_awscostentrylineitem	reservation_amortized_upfront_cost_for_usage
45	AWS	reservation/RecurringFeeForUsage	reporting_awscostentrylineitem	reservation_recurring_fee_for_usage
46	AWS	reservation/UnusedQuantity	reporting_awscostentrylineitem	reservation_unused_quantity
47	AWS	reservation/UnusedRecurringFee	reporting_awscostentrylineitem	reservation_unused_recurring_fee
\.


--
-- Data for Name: si_unit_scale; Type: TABLE DATA; Schema: public; Owner: kokuadmin
--

COPY public.si_unit_scale (id, prefix, prefix_symbol, multiplying_factor) FROM stdin;
1	yotta	Y	1000000000000000000000000.000000000000000000000000
2	zetta	Z	1000000000000000000000.000000000000000000000000
3	exa	E	1000000000000000000.000000000000000000000000
4	peta	P	1000000000000000.000000000000000000000000
5	tera	T	1000000000000.000000000000000000000000
6	giga	G	1000000000.000000000000000000000000
7	mega	M	1000000.000000000000000000000000
8	kilo	k	1000.000000000000000000000000
9			1.000000000000000000000000
10	milli	m	0.001000000000000000000000
11	micro	µ	0.000001000000000000000000
12	nano	n	0.000000001000000000000000
13	pico	p	0.000000000001000000000000
14	femto	f	0.000000000000001000000000
15	atto	a	0.000000000000000001000000
16	zepto	z	0.000000000000000000001000
17	yocto	y	0.000000000000000000000001
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: testcustomer; Owner: kokuadmin
--

COPY testcustomer.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2018-09-18 17:36:29.679868+00
2	auth	0001_initial	2018-09-18 17:36:29.698544+00
3	admin	0001_initial	2018-09-18 17:36:29.713915+00
4	admin	0002_logentry_remove_auto_add	2018-09-18 17:36:29.729283+00
5	admin	0003_logentry_add_action_flag_choices	2018-09-18 17:36:29.74311+00
6	contenttypes	0002_remove_content_type_name	2018-09-18 17:36:29.760112+00
7	auth	0002_alter_permission_name_max_length	2018-09-18 17:36:29.77139+00
8	auth	0003_alter_user_email_max_length	2018-09-18 17:36:29.787431+00
9	auth	0004_alter_user_username_opts	2018-09-18 17:36:29.802143+00
10	auth	0005_alter_user_last_login_null	2018-09-18 17:36:29.816717+00
11	auth	0006_require_contenttypes_0002	2018-09-18 17:36:29.82471+00
12	auth	0007_alter_validators_add_error_messages	2018-09-18 17:36:29.840045+00
13	auth	0008_alter_user_username_max_length	2018-09-18 17:36:29.85461+00
14	auth	0009_alter_user_last_name_max_length	2018-09-18 17:36:29.869515+00
15	api	0001_initial	2018-09-18 17:36:29.878376+00
16	api	0002_auto_20180509_1400	2018-09-18 17:36:29.910066+00
17	api	0003_auto_20180509_1849	2018-09-18 17:36:29.940002+00
18	api	0004_auto_20180510_1824	2018-09-18 17:36:29.976335+00
19	api	0005_auto_20180511_1445	2018-09-18 17:36:30.001131+00
20	api	0006_resettoken	2018-09-18 17:36:30.018313+00
21	api	0007_userpreference	2018-09-18 17:36:30.036025+00
22	api	0008_provider	2018-09-18 17:36:30.108604+00
23	api	0009_auto_20180523_0045	2018-09-18 17:36:30.129415+00
24	api	0010_auto_20180523_1540	2018-09-18 17:36:30.218352+00
25	api	0011_auto_20180524_1838	2018-09-18 17:36:30.237645+00
26	api	0012_auto_20180529_1526	2018-09-18 17:36:30.247088+00
27	api	0013_auto_20180531_1921	2018-09-18 17:36:30.257923+00
28	api	0014_costusagereportstatus	2018-09-18 17:36:30.276929+00
29	api	0015_auto_20180614_1343	2018-09-18 17:36:30.2976+00
30	api	0016_auto_20180802_1911	2018-09-18 17:36:30.31665+00
31	api	0017_auto_20180815_1716	2018-09-18 17:36:30.333618+00
32	api	0018_delete_status	2018-09-18 17:36:30.349516+00
33	api	0019_provider_setup_complete	2018-09-18 17:36:30.36849+00
34	authtoken	0001_initial	2018-09-18 17:36:30.387985+00
35	authtoken	0002_auto_20160226_1747	2018-09-18 17:36:30.426208+00
36	reporting	0001_initial	2018-09-18 17:36:30.579391+00
37	reporting	0002_auto_20180615_1725	2018-09-18 17:36:31.01659+00
38	reporting	0003_auto_20180619_1833	2018-09-18 17:36:31.41731+00
39	reporting	0004_auto_20180803_1926	2018-09-18 17:36:31.454992+00
40	reporting	0005_auto_20180807_1819	2018-09-18 17:36:31.508058+00
41	reporting	0006_auto_20180821_1654	2018-09-18 17:36:31.742303+00
42	reporting	0007_auto_20180824_0035	2018-09-18 17:36:31.90256+00
43	reporting	0008_awsaccountalias	2018-09-18 17:36:31.924084+00
44	reporting_common	0001_initial	2018-09-18 17:36:31.933311+00
45	reporting_common	0002_auto_20180608_1647	2018-09-18 17:36:31.941874+00
46	reporting_common	0003_costusagereportstatus	2018-09-18 17:36:31.962957+00
47	reporting_common	0004_siunitscale	2018-09-18 17:36:31.973298+00
48	reporting_common	0005_auto_20180725_1523	2018-09-18 17:36:31.982094+00
49	reporting_common	0006_auto_20180802_1911	2018-09-18 17:36:31.994709+00
50	reporting_common	0007_auto_20180808_2134	2018-09-18 17:36:32.004751+00
51	sessions	0001_initial	2018-09-18 17:36:32.014884+00
\.


--
-- Data for Name: reporting_awsaccountalias; Type: TABLE DATA; Schema: testcustomer; Owner: kokuadmin
--

COPY testcustomer.reporting_awsaccountalias (id, account_id, account_alias) FROM stdin;
\.


--
-- Data for Name: reporting_awscostentry; Type: TABLE DATA; Schema: testcustomer; Owner: kokuadmin
--

COPY testcustomer.reporting_awscostentry (id, interval_start, interval_end, bill_id) FROM stdin;
\.


--
-- Data for Name: reporting_awscostentrybill; Type: TABLE DATA; Schema: testcustomer; Owner: kokuadmin
--

COPY testcustomer.reporting_awscostentrybill (id, billing_resource, bill_type, payer_account_id, billing_period_start, billing_period_end) FROM stdin;
\.


--
-- Data for Name: reporting_awscostentrylineitem; Type: TABLE DATA; Schema: testcustomer; Owner: kokuadmin
--

COPY testcustomer.reporting_awscostentrylineitem (id, tags, invoice_id, line_item_type, usage_account_id, usage_start, usage_end, product_code, usage_type, operation, availability_zone, resource_id, usage_amount, normalization_factor, normalized_usage_amount, currency_code, unblended_rate, unblended_cost, blended_rate, blended_cost, tax_type, cost_entry_id, cost_entry_bill_id, cost_entry_pricing_id, cost_entry_product_id, cost_entry_reservation_id, hash, public_on_demand_cost, public_on_demand_rate, reservation_amortized_upfront_cost_for_usage, reservation_amortized_upfront_fee, reservation_recurring_fee_for_usage, reservation_unused_quantity, reservation_unused_recurring_fee) FROM stdin;
\.


--
-- Data for Name: reporting_awscostentrylineitem_aggregates; Type: TABLE DATA; Schema: testcustomer; Owner: kokuadmin
--

COPY testcustomer.reporting_awscostentrylineitem_aggregates (id, time_scope_value, report_type, usage_account_id, product_code, region, availability_zone, usage_amount, unblended_cost, resource_count) FROM stdin;
\.


--
-- Data for Name: reporting_awscostentrylineitem_daily; Type: TABLE DATA; Schema: testcustomer; Owner: kokuadmin
--

COPY testcustomer.reporting_awscostentrylineitem_daily (id, line_item_type, usage_account_id, usage_start, product_code, usage_type, operation, availability_zone, resource_id, usage_amount, normalization_factor, normalized_usage_amount, currency_code, unblended_rate, unblended_cost, blended_rate, blended_cost, public_on_demand_cost, public_on_demand_rate, tax_type, tags, cost_entry_pricing_id, cost_entry_product_id, cost_entry_reservation_id) FROM stdin;
\.


--
-- Data for Name: reporting_awscostentrylineitem_daily_summary; Type: TABLE DATA; Schema: testcustomer; Owner: kokuadmin
--

COPY testcustomer.reporting_awscostentrylineitem_daily_summary (id, usage_start, usage_account_id, product_code, product_family, availability_zone, region, instance_type, unit, resource_count, usage_amount, normalization_factor, normalized_usage_amount, currency_code, unblended_rate, unblended_cost, blended_rate, blended_cost, public_on_demand_cost, public_on_demand_rate, tax_type) FROM stdin;
\.


--
-- Data for Name: reporting_awscostentrypricing; Type: TABLE DATA; Schema: testcustomer; Owner: kokuadmin
--

COPY testcustomer.reporting_awscostentrypricing (id, term, unit) FROM stdin;
\.


--
-- Data for Name: reporting_awscostentryproduct; Type: TABLE DATA; Schema: testcustomer; Owner: kokuadmin
--

COPY testcustomer.reporting_awscostentryproduct (id, sku, product_name, product_family, service_code, region, instance_type, memory, vcpu, memory_unit) FROM stdin;
\.


--
-- Data for Name: reporting_awscostentryreservation; Type: TABLE DATA; Schema: testcustomer; Owner: kokuadmin
--

COPY testcustomer.reporting_awscostentryreservation (id, reservation_arn, number_of_reservations, units_per_reservation, start_time, end_time) FROM stdin;
\.


--
-- Name: api_provider_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.api_provider_id_seq', 1, true);


--
-- Name: api_providerauthentication_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.api_providerauthentication_id_seq', 1, true);


--
-- Name: api_providerbillingsource_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.api_providerbillingsource_id_seq', 1, true);


--
-- Name: api_resettoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.api_resettoken_id_seq', 1, true);


--
-- Name: api_tenant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.api_tenant_id_seq', 2, true);


--
-- Name: api_userpreference_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.api_userpreference_id_seq', 3, true);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, true);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 116, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, true);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.auth_user_id_seq', 2, true);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 29, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 51, true);


--
-- Name: region_mapping_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.region_mapping_id_seq', 1, false);


--
-- Name: reporting_common_costusagereportstatus_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.reporting_common_costusagereportstatus_id_seq', 1, false);


--
-- Name: reporting_common_reportcolumnmap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.reporting_common_reportcolumnmap_id_seq', 47, true);


--
-- Name: si_unit_scale_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kokuadmin
--

SELECT pg_catalog.setval('public.si_unit_scale_id_seq', 17, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: testcustomer; Owner: kokuadmin
--

SELECT pg_catalog.setval('testcustomer.django_migrations_id_seq', 51, true);


--
-- Name: reporting_awsaccountalias_id_seq; Type: SEQUENCE SET; Schema: testcustomer; Owner: kokuadmin
--

SELECT pg_catalog.setval('testcustomer.reporting_awsaccountalias_id_seq', 1, false);


--
-- Name: reporting_awscostentry_id_seq; Type: SEQUENCE SET; Schema: testcustomer; Owner: kokuadmin
--

SELECT pg_catalog.setval('testcustomer.reporting_awscostentry_id_seq', 1, false);


--
-- Name: reporting_awscostentrybill_id_seq; Type: SEQUENCE SET; Schema: testcustomer; Owner: kokuadmin
--

SELECT pg_catalog.setval('testcustomer.reporting_awscostentrybill_id_seq', 1, false);


--
-- Name: reporting_awscostentrylineitem_aggregates_id_seq; Type: SEQUENCE SET; Schema: testcustomer; Owner: kokuadmin
--

SELECT pg_catalog.setval('testcustomer.reporting_awscostentrylineitem_aggregates_id_seq', 1, false);


--
-- Name: reporting_awscostentrylineitem_daily_id_seq; Type: SEQUENCE SET; Schema: testcustomer; Owner: kokuadmin
--

SELECT pg_catalog.setval('testcustomer.reporting_awscostentrylineitem_daily_id_seq', 1, false);


--
-- Name: reporting_awscostentrylineitem_daily_summary_id_seq; Type: SEQUENCE SET; Schema: testcustomer; Owner: kokuadmin
--

SELECT pg_catalog.setval('testcustomer.reporting_awscostentrylineitem_daily_summary_id_seq', 1, false);


--
-- Name: reporting_awscostentrylineitem_id_seq; Type: SEQUENCE SET; Schema: testcustomer; Owner: kokuadmin
--

SELECT pg_catalog.setval('testcustomer.reporting_awscostentrylineitem_id_seq', 1, false);


--
-- Name: reporting_awscostentrypricing_id_seq; Type: SEQUENCE SET; Schema: testcustomer; Owner: kokuadmin
--

SELECT pg_catalog.setval('testcustomer.reporting_awscostentrypricing_id_seq', 1, false);


--
-- Name: reporting_awscostentryproduct_id_seq; Type: SEQUENCE SET; Schema: testcustomer; Owner: kokuadmin
--

SELECT pg_catalog.setval('testcustomer.reporting_awscostentryproduct_id_seq', 1, false);


--
-- Name: reporting_awscostentryreservation_id_seq; Type: SEQUENCE SET; Schema: testcustomer; Owner: kokuadmin
--

SELECT pg_catalog.setval('testcustomer.reporting_awscostentryreservation_id_seq', 1, false);


--
-- Name: api_customer api_customer_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_customer
    ADD CONSTRAINT api_customer_pkey PRIMARY KEY (group_ptr_id);


--
-- Name: api_customer api_customer_schema_name_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_customer
    ADD CONSTRAINT api_customer_schema_name_key UNIQUE (schema_name);


--
-- Name: api_customer api_customer_uuid_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_customer
    ADD CONSTRAINT api_customer_uuid_key UNIQUE (uuid);


--
-- Name: api_provider api_provider_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_provider
    ADD CONSTRAINT api_provider_pkey PRIMARY KEY (id);


--
-- Name: api_provider api_provider_uuid_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_provider
    ADD CONSTRAINT api_provider_uuid_key UNIQUE (uuid);


--
-- Name: api_providerauthentication api_providerauthentication_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_providerauthentication
    ADD CONSTRAINT api_providerauthentication_pkey PRIMARY KEY (id);


--
-- Name: api_providerauthentication api_providerauthentication_provider_resource_name_fa7deecb_uniq; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_providerauthentication
    ADD CONSTRAINT api_providerauthentication_provider_resource_name_fa7deecb_uniq UNIQUE (provider_resource_name);


--
-- Name: api_providerauthentication api_providerauthentication_uuid_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_providerauthentication
    ADD CONSTRAINT api_providerauthentication_uuid_key UNIQUE (uuid);


--
-- Name: api_providerbillingsource api_providerbillingsource_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_providerbillingsource
    ADD CONSTRAINT api_providerbillingsource_pkey PRIMARY KEY (id);


--
-- Name: api_providerbillingsource api_providerbillingsource_uuid_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_providerbillingsource
    ADD CONSTRAINT api_providerbillingsource_uuid_key UNIQUE (uuid);


--
-- Name: api_resettoken api_resettoken_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_resettoken
    ADD CONSTRAINT api_resettoken_pkey PRIMARY KEY (id);


--
-- Name: api_resettoken api_resettoken_token_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_resettoken
    ADD CONSTRAINT api_resettoken_token_key UNIQUE (token);


--
-- Name: api_tenant api_tenant_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_tenant
    ADD CONSTRAINT api_tenant_pkey PRIMARY KEY (id);


--
-- Name: api_tenant api_tenant_schema_name_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_tenant
    ADD CONSTRAINT api_tenant_schema_name_key UNIQUE (schema_name);


--
-- Name: api_user api_user_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_user
    ADD CONSTRAINT api_user_pkey PRIMARY KEY (user_ptr_id);


--
-- Name: api_user api_user_uuid_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_user
    ADD CONSTRAINT api_user_uuid_key UNIQUE (uuid);


--
-- Name: api_userpreference api_userpreference_name_user_id_9f2a465b_uniq; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_userpreference
    ADD CONSTRAINT api_userpreference_name_user_id_9f2a465b_uniq UNIQUE (name, user_id);


--
-- Name: api_userpreference api_userpreference_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_userpreference
    ADD CONSTRAINT api_userpreference_pkey PRIMARY KEY (id);


--
-- Name: api_userpreference api_userpreference_uuid_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_userpreference
    ADD CONSTRAINT api_userpreference_uuid_key UNIQUE (uuid);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);


--
-- Name: auth_user auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);


--
-- Name: auth_user auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: authtoken_token authtoken_token_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_pkey PRIMARY KEY (key);


--
-- Name: authtoken_token authtoken_token_user_id_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_key UNIQUE (user_id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: region_mapping region_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.region_mapping
    ADD CONSTRAINT region_mapping_pkey PRIMARY KEY (id);


--
-- Name: region_mapping region_mapping_region_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.region_mapping
    ADD CONSTRAINT region_mapping_region_key UNIQUE (region);


--
-- Name: region_mapping region_mapping_region_name_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.region_mapping
    ADD CONSTRAINT region_mapping_region_name_key UNIQUE (region_name);


--
-- Name: reporting_common_costusagereportstatus reporting_common_costusagereportstatus_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.reporting_common_costusagereportstatus
    ADD CONSTRAINT reporting_common_costusagereportstatus_pkey PRIMARY KEY (id);


--
-- Name: reporting_common_costusagereportstatus reporting_common_costusagereportstatus_report_name_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.reporting_common_costusagereportstatus
    ADD CONSTRAINT reporting_common_costusagereportstatus_report_name_key UNIQUE (report_name);


--
-- Name: reporting_common_reportcolumnmap reporting_common_reportcolumnmap_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.reporting_common_reportcolumnmap
    ADD CONSTRAINT reporting_common_reportcolumnmap_pkey PRIMARY KEY (id);


--
-- Name: reporting_common_reportcolumnmap reporting_common_reportcolumnmap_provider_column_name_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.reporting_common_reportcolumnmap
    ADD CONSTRAINT reporting_common_reportcolumnmap_provider_column_name_key UNIQUE (provider_column_name);


--
-- Name: si_unit_scale si_unit_scale_pkey; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.si_unit_scale
    ADD CONSTRAINT si_unit_scale_pkey PRIMARY KEY (id);


--
-- Name: si_unit_scale si_unit_scale_prefix_key; Type: CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.si_unit_scale
    ADD CONSTRAINT si_unit_scale_prefix_key UNIQUE (prefix);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: reporting_awsaccountalias reporting_awsaccountalias_account_id_key; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awsaccountalias
    ADD CONSTRAINT reporting_awsaccountalias_account_id_key UNIQUE (account_id);


--
-- Name: reporting_awsaccountalias reporting_awsaccountalias_pkey; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awsaccountalias
    ADD CONSTRAINT reporting_awsaccountalias_pkey PRIMARY KEY (id);


--
-- Name: reporting_awscostentry reporting_awscostentry_pkey; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentry
    ADD CONSTRAINT reporting_awscostentry_pkey PRIMARY KEY (id);


--
-- Name: reporting_awscostentrybill reporting_awscostentrybill_pkey; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrybill
    ADD CONSTRAINT reporting_awscostentrybill_pkey PRIMARY KEY (id);


--
-- Name: reporting_awscostentrylineitem_aggregates reporting_awscostentrylineitem_aggregates_pkey; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem_aggregates
    ADD CONSTRAINT reporting_awscostentrylineitem_aggregates_pkey PRIMARY KEY (id);


--
-- Name: reporting_awscostentrylineitem_daily reporting_awscostentrylineitem_daily_pkey; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem_daily
    ADD CONSTRAINT reporting_awscostentrylineitem_daily_pkey PRIMARY KEY (id);


--
-- Name: reporting_awscostentrylineitem_daily_summary reporting_awscostentrylineitem_daily_summary_pkey; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem_daily_summary
    ADD CONSTRAINT reporting_awscostentrylineitem_daily_summary_pkey PRIMARY KEY (id);


--
-- Name: reporting_awscostentrylineitem reporting_awscostentrylineitem_hash_cost_entry_id_f3893306_uniq; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem
    ADD CONSTRAINT reporting_awscostentrylineitem_hash_cost_entry_id_f3893306_uniq UNIQUE (hash, cost_entry_id);


--
-- Name: reporting_awscostentrylineitem reporting_awscostentrylineitem_pkey; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem
    ADD CONSTRAINT reporting_awscostentrylineitem_pkey PRIMARY KEY (id);


--
-- Name: reporting_awscostentryproduct reporting_awscostentrypr_sku_product_name_region_fea902ae_uniq; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentryproduct
    ADD CONSTRAINT reporting_awscostentrypr_sku_product_name_region_fea902ae_uniq UNIQUE (sku, product_name, region);


--
-- Name: reporting_awscostentrypricing reporting_awscostentrypricing_pkey; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrypricing
    ADD CONSTRAINT reporting_awscostentrypricing_pkey PRIMARY KEY (id);


--
-- Name: reporting_awscostentrypricing reporting_awscostentrypricing_term_unit_c3978af3_uniq; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrypricing
    ADD CONSTRAINT reporting_awscostentrypricing_term_unit_c3978af3_uniq UNIQUE (term, unit);


--
-- Name: reporting_awscostentryproduct reporting_awscostentryproduct_pkey; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentryproduct
    ADD CONSTRAINT reporting_awscostentryproduct_pkey PRIMARY KEY (id);


--
-- Name: reporting_awscostentryreservation reporting_awscostentryreservation_pkey; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentryreservation
    ADD CONSTRAINT reporting_awscostentryreservation_pkey PRIMARY KEY (id);


--
-- Name: reporting_awscostentryreservation reporting_awscostentryreservation_reservation_arn_key; Type: CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentryreservation
    ADD CONSTRAINT reporting_awscostentryreservation_reservation_arn_key UNIQUE (reservation_arn);


--
-- Name: api_customer_owner_id_c1534767; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX api_customer_owner_id_c1534767 ON public.api_customer USING btree (owner_id);


--
-- Name: api_customer_schema_name_6b716c4b_like; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX api_customer_schema_name_6b716c4b_like ON public.api_customer USING btree (schema_name text_pattern_ops);


--
-- Name: api_provider_authentication_id_201fd4b9; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX api_provider_authentication_id_201fd4b9 ON public.api_provider USING btree (authentication_id);


--
-- Name: api_provider_billing_source_id_cb6b5a6f; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX api_provider_billing_source_id_cb6b5a6f ON public.api_provider USING btree (billing_source_id);


--
-- Name: api_provider_created_by_id_e740fc35; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX api_provider_created_by_id_e740fc35 ON public.api_provider USING btree (created_by_id);


--
-- Name: api_provider_customer_id_87062290; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX api_provider_customer_id_87062290 ON public.api_provider USING btree (customer_id);


--
-- Name: api_providerauthentication_provider_resource_name_fa7deecb_like; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX api_providerauthentication_provider_resource_name_fa7deecb_like ON public.api_providerauthentication USING btree (provider_resource_name text_pattern_ops);


--
-- Name: api_resettoken_user_id_4b3d42c0; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX api_resettoken_user_id_4b3d42c0 ON public.api_resettoken USING btree (user_id);


--
-- Name: api_tenant_schema_name_733d339b_like; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX api_tenant_schema_name_733d339b_like ON public.api_tenant USING btree (schema_name varchar_pattern_ops);


--
-- Name: api_userpreference_user_id_e62eaffa; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX api_userpreference_user_id_e62eaffa ON public.api_userpreference USING btree (user_id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: auth_user_groups_group_id_97559544; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX auth_user_groups_group_id_97559544 ON public.auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_user_id_6a12ed8b; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON public.auth_user_groups USING btree (user_id);


--
-- Name: auth_user_user_permissions_permission_id_1fbb5f2c; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON public.auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_user_id_a95ead1b; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON public.auth_user_user_permissions USING btree (user_id);


--
-- Name: auth_user_username_6821ab7c_like; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX auth_user_username_6821ab7c_like ON public.auth_user USING btree (username varchar_pattern_ops);


--
-- Name: authtoken_token_key_10f0b77e_like; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX authtoken_token_key_10f0b77e_like ON public.authtoken_token USING btree (key varchar_pattern_ops);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: region_mapping_region_9c0d71ba_like; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX region_mapping_region_9c0d71ba_like ON public.region_mapping USING btree (region varchar_pattern_ops);


--
-- Name: region_mapping_region_name_ad295b89_like; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX region_mapping_region_name_ad295b89_like ON public.region_mapping USING btree (region_name varchar_pattern_ops);


--
-- Name: reporting_common_costusa_report_name_134674b5_like; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX reporting_common_costusa_report_name_134674b5_like ON public.reporting_common_costusagereportstatus USING btree (report_name varchar_pattern_ops);


--
-- Name: reporting_common_costusagereportstatus_provider_id_f012c75a; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX reporting_common_costusagereportstatus_provider_id_f012c75a ON public.reporting_common_costusagereportstatus USING btree (provider_id);


--
-- Name: reporting_common_reportc_provider_column_name_e01eaba3_like; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX reporting_common_reportc_provider_column_name_e01eaba3_like ON public.reporting_common_reportcolumnmap USING btree (provider_column_name varchar_pattern_ops);


--
-- Name: si_unit_scale_prefix_eb9daade_like; Type: INDEX; Schema: public; Owner: kokuadmin
--

CREATE INDEX si_unit_scale_prefix_eb9daade_like ON public.si_unit_scale USING btree (prefix varchar_pattern_ops);


--
-- Name: interval_start_idx; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX interval_start_idx ON testcustomer.reporting_awscostentry USING btree (interval_start);


--
-- Name: product_code_idx; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX product_code_idx ON testcustomer.reporting_awscostentrylineitem_daily USING btree (product_code);


--
-- Name: region_idx; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX region_idx ON testcustomer.reporting_awscostentryproduct USING btree (region);


--
-- Name: reporting_awsaccountalias_account_id_85724b8c_like; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX reporting_awsaccountalias_account_id_85724b8c_like ON testcustomer.reporting_awsaccountalias USING btree (account_id varchar_pattern_ops);


--
-- Name: reporting_awscostentry_bill_id_017f27a3; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX reporting_awscostentry_bill_id_017f27a3 ON testcustomer.reporting_awscostentry USING btree (bill_id);


--
-- Name: reporting_awscostentryline_cost_entry_pricing_id_5a6a9b38; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX reporting_awscostentryline_cost_entry_pricing_id_5a6a9b38 ON testcustomer.reporting_awscostentrylineitem_daily USING btree (cost_entry_pricing_id);


--
-- Name: reporting_awscostentryline_cost_entry_product_id_4d8ef2fd; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX reporting_awscostentryline_cost_entry_product_id_4d8ef2fd ON testcustomer.reporting_awscostentrylineitem_daily USING btree (cost_entry_product_id);


--
-- Name: reporting_awscostentryline_cost_entry_reservation_id_13b1cb08; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX reporting_awscostentryline_cost_entry_reservation_id_13b1cb08 ON testcustomer.reporting_awscostentrylineitem_daily USING btree (cost_entry_reservation_id);


--
-- Name: reporting_awscostentryline_cost_entry_reservation_id_9332b371; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX reporting_awscostentryline_cost_entry_reservation_id_9332b371 ON testcustomer.reporting_awscostentrylineitem USING btree (cost_entry_reservation_id);


--
-- Name: reporting_awscostentrylineitem_cost_entry_bill_id_5ae74e09; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX reporting_awscostentrylineitem_cost_entry_bill_id_5ae74e09 ON testcustomer.reporting_awscostentrylineitem USING btree (cost_entry_bill_id);


--
-- Name: reporting_awscostentrylineitem_cost_entry_id_4d1a7fc4; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX reporting_awscostentrylineitem_cost_entry_id_4d1a7fc4 ON testcustomer.reporting_awscostentrylineitem USING btree (cost_entry_id);


--
-- Name: reporting_awscostentrylineitem_cost_entry_pricing_id_a654a7e3; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX reporting_awscostentrylineitem_cost_entry_pricing_id_a654a7e3 ON testcustomer.reporting_awscostentrylineitem USING btree (cost_entry_pricing_id);


--
-- Name: reporting_awscostentrylineitem_cost_entry_product_id_29c80210; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX reporting_awscostentrylineitem_cost_entry_product_id_29c80210 ON testcustomer.reporting_awscostentrylineitem USING btree (cost_entry_product_id);


--
-- Name: reporting_awscostentryreservation_reservation_arn_e387aa5b_like; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX reporting_awscostentryreservation_reservation_arn_e387aa5b_like ON testcustomer.reporting_awscostentryreservation USING btree (reservation_arn text_pattern_ops);


--
-- Name: summary_product_code_idx; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX summary_product_code_idx ON testcustomer.reporting_awscostentrylineitem_daily_summary USING btree (product_code);


--
-- Name: summary_usage_account_id_idx; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX summary_usage_account_id_idx ON testcustomer.reporting_awscostentrylineitem_daily_summary USING btree (usage_account_id);


--
-- Name: summary_usage_start_idx; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX summary_usage_start_idx ON testcustomer.reporting_awscostentrylineitem_daily_summary USING btree (usage_start);


--
-- Name: usage_account_id_idx; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX usage_account_id_idx ON testcustomer.reporting_awscostentrylineitem_daily USING btree (usage_account_id);


--
-- Name: usage_start_idx; Type: INDEX; Schema: testcustomer; Owner: kokuadmin
--

CREATE INDEX usage_start_idx ON testcustomer.reporting_awscostentrylineitem_daily USING btree (usage_start);


--
-- Name: api_customer api_customer_group_ptr_id_fe96eec5_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_customer
    ADD CONSTRAINT api_customer_group_ptr_id_fe96eec5_fk_auth_group_id FOREIGN KEY (group_ptr_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: api_customer api_customer_owner_id_c1534767_fk_api_user_user_ptr_id; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_customer
    ADD CONSTRAINT api_customer_owner_id_c1534767_fk_api_user_user_ptr_id FOREIGN KEY (owner_id) REFERENCES public.api_user(user_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: api_provider api_provider_authentication_id_201fd4b9_fk_api_provi; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_provider
    ADD CONSTRAINT api_provider_authentication_id_201fd4b9_fk_api_provi FOREIGN KEY (authentication_id) REFERENCES public.api_providerauthentication(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: api_provider api_provider_billing_source_id_cb6b5a6f_fk_api_provi; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_provider
    ADD CONSTRAINT api_provider_billing_source_id_cb6b5a6f_fk_api_provi FOREIGN KEY (billing_source_id) REFERENCES public.api_providerbillingsource(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: api_provider api_provider_created_by_id_e740fc35_fk_api_user_user_ptr_id; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_provider
    ADD CONSTRAINT api_provider_created_by_id_e740fc35_fk_api_user_user_ptr_id FOREIGN KEY (created_by_id) REFERENCES public.api_user(user_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: api_provider api_provider_customer_id_87062290_fk_api_customer_group_ptr_id; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_provider
    ADD CONSTRAINT api_provider_customer_id_87062290_fk_api_customer_group_ptr_id FOREIGN KEY (customer_id) REFERENCES public.api_customer(group_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: api_resettoken api_resettoken_user_id_4b3d42c0_fk_api_user_user_ptr_id; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_resettoken
    ADD CONSTRAINT api_resettoken_user_id_4b3d42c0_fk_api_user_user_ptr_id FOREIGN KEY (user_id) REFERENCES public.api_user(user_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: api_user api_user_user_ptr_id_5a766ead_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_user
    ADD CONSTRAINT api_user_user_ptr_id_5a766ead_fk_auth_user_id FOREIGN KEY (user_ptr_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: api_userpreference api_userpreference_user_id_e62eaffa_fk_api_user_user_ptr_id; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.api_userpreference
    ADD CONSTRAINT api_userpreference_user_id_e62eaffa_fk_api_user_user_ptr_id FOREIGN KEY (user_id) REFERENCES public.api_user(user_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: authtoken_token authtoken_token_user_id_35299eff_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_35299eff_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reporting_common_costusagereportstatus reporting_common_cos_provider_id_f012c75a_fk_api_provi; Type: FK CONSTRAINT; Schema: public; Owner: kokuadmin
--

ALTER TABLE ONLY public.reporting_common_costusagereportstatus
    ADD CONSTRAINT reporting_common_cos_provider_id_f012c75a_fk_api_provi FOREIGN KEY (provider_id) REFERENCES public.api_provider(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reporting_awscostentry reporting_awscostent_bill_id_017f27a3_fk_reporting; Type: FK CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentry
    ADD CONSTRAINT reporting_awscostent_bill_id_017f27a3_fk_reporting FOREIGN KEY (bill_id) REFERENCES testcustomer.reporting_awscostentrybill(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reporting_awscostentrylineitem reporting_awscostent_cost_entry_bill_id_5ae74e09_fk_reporting; Type: FK CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem
    ADD CONSTRAINT reporting_awscostent_cost_entry_bill_id_5ae74e09_fk_reporting FOREIGN KEY (cost_entry_bill_id) REFERENCES testcustomer.reporting_awscostentrybill(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reporting_awscostentrylineitem reporting_awscostent_cost_entry_id_4d1a7fc4_fk_reporting; Type: FK CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem
    ADD CONSTRAINT reporting_awscostent_cost_entry_id_4d1a7fc4_fk_reporting FOREIGN KEY (cost_entry_id) REFERENCES testcustomer.reporting_awscostentry(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reporting_awscostentrylineitem_daily reporting_awscostent_cost_entry_pricing_i_5a6a9b38_fk_reporting; Type: FK CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem_daily
    ADD CONSTRAINT reporting_awscostent_cost_entry_pricing_i_5a6a9b38_fk_reporting FOREIGN KEY (cost_entry_pricing_id) REFERENCES testcustomer.reporting_awscostentrypricing(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reporting_awscostentrylineitem reporting_awscostent_cost_entry_pricing_i_a654a7e3_fk_reporting; Type: FK CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem
    ADD CONSTRAINT reporting_awscostent_cost_entry_pricing_i_a654a7e3_fk_reporting FOREIGN KEY (cost_entry_pricing_id) REFERENCES testcustomer.reporting_awscostentrypricing(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reporting_awscostentrylineitem reporting_awscostent_cost_entry_product_i_29c80210_fk_reporting; Type: FK CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem
    ADD CONSTRAINT reporting_awscostent_cost_entry_product_i_29c80210_fk_reporting FOREIGN KEY (cost_entry_product_id) REFERENCES testcustomer.reporting_awscostentryproduct(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reporting_awscostentrylineitem_daily reporting_awscostent_cost_entry_product_i_4d8ef2fd_fk_reporting; Type: FK CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem_daily
    ADD CONSTRAINT reporting_awscostent_cost_entry_product_i_4d8ef2fd_fk_reporting FOREIGN KEY (cost_entry_product_id) REFERENCES testcustomer.reporting_awscostentryproduct(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reporting_awscostentrylineitem_daily reporting_awscostent_cost_entry_reservati_13b1cb08_fk_reporting; Type: FK CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem_daily
    ADD CONSTRAINT reporting_awscostent_cost_entry_reservati_13b1cb08_fk_reporting FOREIGN KEY (cost_entry_reservation_id) REFERENCES testcustomer.reporting_awscostentryreservation(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reporting_awscostentrylineitem reporting_awscostent_cost_entry_reservati_9332b371_fk_reporting; Type: FK CONSTRAINT; Schema: testcustomer; Owner: kokuadmin
--

ALTER TABLE ONLY testcustomer.reporting_awscostentrylineitem
    ADD CONSTRAINT reporting_awscostent_cost_entry_reservati_9332b371_fk_reporting FOREIGN KEY (cost_entry_reservation_id) REFERENCES testcustomer.reporting_awscostentryreservation(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

